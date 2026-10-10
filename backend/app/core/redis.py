from typing import AsyncGenerator
from redis.asyncio import ConnectionPool, Redis
from core.config import settings

pool = ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    decode_responses=True,
)
redis_client = Redis(connection_pool=pool)


def get_redis() -> Redis:
    return redis_client