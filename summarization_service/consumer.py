import asyncio

import logging
import httpx
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from pydantic import ValidationError

from config import settings
from schemas import SummaryRequest, SummaryResponse
from summarizer import generate_summary

logger = logging.getLogger(__name__)


async def process_message(
    msg,
    producer: AIOKafkaProducer,
    client: httpx.AsyncClient,
) -> None:
    task = SummaryRequest.model_validate_json(msg.value)

    summary_text = await generate_summary(client, task.username, task.tasks)
    result = SummaryResponse(
        user_id=task.user_id,
        email=task.email,
        username=task.username,
        summary_text=summary_text,
    )

    await producer.send_and_wait(
        settings.KAFKA_SUMMARY_RESPONSE_TOPIC,
        key=str(task.user_id).encode("utf-8"),
        value=result.model_dump_json().encode("utf-8"),
    )


async def run_consumer(client: httpx.AsyncClient) -> None:
    consumer = AIOKafkaConsumer(
        settings.KAFKA_SUMMARY_REQUEST_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
        enable_auto_commit=False,
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
    )
    try:
        await consumer.start()
        await producer.start()
        logger.info("🚀 Воркер суммаризации запущен и слушает топик: %s", settings.KAFKA_SUMMARY_REQUEST_TOPIC)

        async for msg in consumer:
            logger.info("📥 Получено новое сообщение из Kafka!")
            for attempt in range(3):
                try:
                    await process_message(msg, producer, client)
                    await consumer.commit()
                    break  # ✅ Успешно обработали — выходим из цикла повторов
                except (httpx.RequestError, httpx.HTTPStatusError) as e:
                    logger.warning(f"Сетевая ошибка (попытка {attempt + 1}/3): {e}")
                    if attempt < 2:
                        await asyncio.sleep(2)
                    else:
                        logger.error("Все попытки исчерпаны, пропускаем сообщение")
                        # При желании здесь можно отправить msg.value в топик DLQ
                        await consumer.commit()
                except ValidationError:
                    logger.error("Ошибка сериализации данных, сообщение исключено")
                    await consumer.commit()
                    break  # 🗑️ Битые данные не повторяем — сразу выходим
                except Exception as e:
                    logger.exception(f"Непредвиденная ошибка при обработке: {e}")
                    break  # 🛑 Не зацикливаемся на багах в коде
    finally:
        await consumer.stop()
        await producer.stop()