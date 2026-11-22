from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict
ROOT_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    GROQ_API_KEY: str
    GROQ_MODEL: str = "openai/gpt-oss-120b"
    GROQ_API_URL: str = "https://api.groq.com/openai/v1/chat/completions"

    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_SUMMARY_REQUEST_TOPIC: str = "summary.requests"
    KAFKA_SUMMARY_RESPONSE_TOPIC: str = "summary.responses"
    KAFKA_GROUP_ID: str = "summarization_service_group"

settings = Settings()