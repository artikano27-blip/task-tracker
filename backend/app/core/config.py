from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
  model_config = SettingsConfigDict(
      env_file=ROOT_DIR / ".env", env_file_encoding="utf-8", extra="ignore"
  )

  # База данных PostgreSQL (для asyncpg / SQLAlchemy)
  DATABASE_URL: str = (
      "postgresql+asyncpg://postgres:postgres@localhost:5432/task_db"
  )

  # Подключение к Kafka
  # По умолчанию localhost для локального запуска; в Docker переопределится через .env
  KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
  KAFKA_MODERATED_TOPIC: str = "meme_moderated"
  KAFKA_BACKEND_GROUP_ID: str = "backend_moderation_group"

  REDIS_HOST: str = "localhost"
  REDIS_PORT: int = 6379
  SECRET_KEY: str = Field(...)
  ALGORITHM: str = "HS256"
  ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
  REFRESH_TOKEN_EXPIRE_DAYS: int = 30
settings = Settings()