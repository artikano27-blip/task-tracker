import logging
import asyncio
import json
from aiokafka import AIOKafkaConsumer
from pydantic import ValidationError
from app.core.config import settings
from app.tasks.email import send_summary_email
from app.schemas.summary import SummaryResponse

logger = logging.getLogger(__name__)


async def run_consumer():
    consumer = AIOKafkaConsumer(
        settings.KAFKA_SUMMARY_RESPONSE_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_BACKEND_GROUP_ID,
        enable_auto_commit=False,
    )
    await consumer.start()
    logger.info("🎧 Слушатель summary_consumer запущен...")
    try:
        async for msg in consumer:
            try:
                data = json.loads(msg.value)
                response = SummaryResponse.model_validate(data)

            except (json.JSONDecodeError, ValidationError):
                logger.error("Ошибка десериализации данных, ответ исключён")
                await consumer.commit()
                continue

            send_summary_email.delay(
                email=response.email,
                username=response.username,
                summary_text=response.summary_text
            )
            await consumer.commit()
            logger.info(f"✅ Ответ обработан и отправлен в очередь")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(run_consumer())
