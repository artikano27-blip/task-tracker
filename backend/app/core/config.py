from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
      env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
  )

  # База данных PostgreSQL (для asyncpg / SQLAlchemy)
  DATABASE_URL: str = (
      "postgresql+asyncpg://postgres:postgres@localhost:5432/task_db"
  )
  DEFAULT_COLUMNS: tuple[str, ...] = ("К выполнению", "В работе", "Готово")
  # Подключение к Kafka
  # По умолчанию localhost для локального запуска; в Docker переопределится через .env
  KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
  KAFKA_SUMMARY_REQUEST_TOPIC: str = "summary.requests"
  KAFKA_SUMMARY_RESPONSE_TOPIC: str = "summary.responses"
  KAFKA_BACKEND_GROUP_ID: str = "backend_summary_group"
  FRONTEND_URL: str = "http://localhost"
  SMTP_HOST: str = "smtp.yandex.ru"
  SMTP_PORT: int = 465
  SMTP_USER: str = Field(...)
  SMTP_PASSWORD: str = Field(...)
  SMTP_FROM_EMAIL: str = Field(...)


  REDIS_HOST: str = "localhost"
  REDIS_PORT: int = 6379
  SECRET_KEY: str = Field(...)
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
  REFRESH_TOKEN_EXPIRE_DAYS: int = 30
  CELERY_BROKER_URL: str = "amqp://guest:guest@rabbitmq:5672//"

  MAX_SESSIONS_COUNT: int = 5
settings = Settings()