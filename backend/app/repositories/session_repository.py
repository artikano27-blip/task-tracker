from datetime import datetime, timezone, timedelta
import uuid

from redis.asyncio import Redis

from app.core.config import settings
from app.schemas.token import SessionData


class SessionRepository:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def create_session(self, user_id: uuid.UUID, jti: str) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        session_key = f"session:{jti}"
        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        session = SessionData(status="active", jti=jti)
        now_ts = datetime.now(timezone.utc).timestamp()

        async with self.redis.pipeline(transaction=True) as pipe:
            # noinspection PyAsyncCall
            pipe.zadd(user_sessions_key, {jti: now_ts})
            # noinspection PyAsyncCall
            pipe.expire(user_sessions_key, ttl_seconds)
            # noinspection PyAsyncCall
            pipe.set(
                name=session_key,
                value=session.model_dump_json(),
                ex=ttl_seconds,
            )
            await pipe.execute()

    async def rotate_session(
            self,
            user_id: uuid.UUID,
            old_session: SessionData,
            new_jti: str,
            access_token: str,
            refresh_token: str,
    ) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        old_session_key = f"session:{old_session.jti}"
        new_session_key = f"session:{new_jti}"

        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        now = datetime.now(timezone.utc)

        # 1. Готовим данные для старой сессии (used + короткий TTL на 1 день)
        marked_old_session = SessionData(
            status="used",
            rotated_at=now,
            access_token=access_token,
            refresh_token=refresh_token,
            jti=old_session.jti,
        )

        # 2. Готовим данные для новой сессии (active + полный TTL)
        new_session = SessionData(
            status="active",
            jti=new_jti,
        )

        async with self.redis.pipeline(transaction=True) as pipe:
            # Убираем старый jti из счетчика сессий пользователя
            # noinspection PyAsyncCall
            pipe.zrem(user_sessions_key, old_session.jti)

            # Добавляем новый jti в счетчик с текущим временем
            # noinspection PyAsyncCall
            pipe.zadd(user_sessions_key, {new_jti: now.timestamp()})

            # Продлеваем жизнь общему счетчику
            # noinspection PyAsyncCall
            pipe.expire(user_sessions_key, ttl_seconds)

            # Переводим старую сессию в "used" с коротким TTL (1 день)
            # noinspection PyAsyncCall
            pipe.set(
                name=old_session_key,
                value=marked_old_session.model_dump_json(),
                ex=timedelta(days=1),
                xx=True,
            )

            # Создаем новую активную сессию с полным сроком жизни
            # noinspection PyAsyncCall
            pipe.set(
                name=new_session_key,
                value=new_session.model_dump_json(),
                ex=ttl_seconds,
            )

            await pipe.execute()

    async def delete_session(self, user_id: uuid.UUID, jti: str) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        session_key = f"session:{jti}"
        session = SessionData(status="revoked", jti=jti)
        async with self.redis.pipeline(transaction=True) as pipe:
            # noinspection PyAsyncCall
            pipe.zrem(user_sessions_key, jti)
            # noinspection PyAsyncCall
            pipe.set(name=session_key, value=session.model_dump_json(), keepttl=True, xx=True)
            await pipe.execute()

    async def revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        user_sessions_key = f"user_sessions:{user_id}"

        jtis = await self.redis.zrange(user_sessions_key, 0, -1)

        keys_to_delete = [f"session:{jti}" for jti in jtis]
        keys_to_delete.append(user_sessions_key)

        await self.redis.delete(*keys_to_delete)

    async def get_sessions_count(self, user_id: uuid.UUID) -> int:
        user_sessions_key = f"user_sessions:{user_id}"
        return await self.redis.zcard(user_sessions_key)

    async def get_session_by_jti(self, jti: str) -> SessionData | None:
        session_key = f"session:{jti}"
        raw_data = await self.redis.get(session_key)
        if not raw_data:
            return None
        return SessionData.model_validate_json(raw_data)
