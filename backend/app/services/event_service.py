import json
import logging
import uuid

from confluent_kafka import Producer

from app.core.config import settings

logger = logging.getLogger(__name__)

class EventService:
    def __init__(self):
        # Не создаем продюсер сразу, чтобы не ломать потоки при fork() в Celery
        self._producer = None

    @property
    def producer(self) -> Producer:
        """Ленивая инициализация продюсера внутри текущего процесса воркера."""
        if self._producer is None:
            self._producer = Producer({
                "bootstrap.servers": settings.KAFKA_BOOTSTRAP_SERVERS,
                "client.id": "backend-summary-producer",
                "acks": "all",
            })
        return self._producer

    def publish_summary_request(
        self,
        user_id: uuid.UUID,
        email: str,
        username: str,
        ready_tasks: dict
    ) -> None:
        payload = {
            "user_id": str(user_id),
            "email": email,
            "username": username,
            "tasks": ready_tasks,
        }

        self.producer.produce(
            topic=settings.KAFKA_SUMMARY_REQUEST_TOPIC,
            key=str(user_id),
            value=json.dumps(payload).encode("utf-8"),
            callback=self._delivery_callback,
        )
        unflushed = self.producer.flush(timeout=10.0)
        if unflushed > 0:
            msg = f"Не удалось доставить {unflushed} сообщений в Kafka за отведённый таймаут"
            logger.error(msg)
            raise TimeoutError(msg)

    @staticmethod
    def _delivery_callback(err, msg):
        if err is not None:
            logger.error(f"Kafka delivery failed: {err}")
        else:
            logger.info(f"Event delivered to {msg.topic()} [{msg.partition()}]")

event_service = EventService()