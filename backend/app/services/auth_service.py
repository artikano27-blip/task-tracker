
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone, timedelta

from pydantic import ValidationError
from redis.asyncio import Redis

from core.config import settings
from core.exceptions import UserAlreadyExistsError, UserEmailAlreadyExistsError, \
    InvalidCredentialsError, InvalidTokenError, TokenCompromisedError
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from models import User
from repositories.user_repository import UserRepository
from schemas import UserCreate
from schemas.token import TokenResponse, TokenPayload, SessionData
from schemas.user import UserLogin

@dataclass
class AuthResult:
    user: User
    access_token: str
    refresh_token: str

class AuthService:
    def __init__(self, user_repo: UserRepository, redis: Redis):
        self.user_repo = user_repo
        self.redis = redis

    @staticmethod
    def _parse_token(token: str) -> TokenPayload:
        raw_payload = decode_token(token)
        try:
            return TokenPayload.model_validate(raw_payload)
        except ValidationError:
            raise InvalidTokenError

    async def _create_session(self, user_id: uuid.UUID, jti: str) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        session_key = f"session:{jti}"
        ttl_seconds = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        await self.redis.sadd(user_sessions_key, jti)
        await self.redis.set(name=session_key, value="active", ex=ttl_seconds)

    async def _delete_session(self, user_id: uuid.UUID, jti: str) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        session_key = f"session:{jti}"
        await self.redis.srem(user_sessions_key, jti)
        await self.redis.set(name=session_key, value="used", keepttl=True)

    async def _get_session_by_jti(self, jti: str) -> SessionData | None:
        session_key = f"session:{jti}"
        raw_data = await self.redis.get(session_key)
        if not raw_data:
            return None
        return SessionData.model_validate_json(raw_data)

    async def _revoke_all_sessions(self, user_id: uuid.UUID) -> None:
        user_sessions_key = f"user_sessions:{user_id}"
        jtis = await self.redis.smembers(user_sessions_key)
        if jtis:
            session_keys = [f"session:{jti}" for jti in jtis]
            await self.redis.delete(*session_keys, user_sessions_key)

    async def _mark_session_used(self, session: SessionData, access_token: str, refresh_token: str) -> None:
        session_key = f"session:{session.jti}"
        now = datetime.now(timezone.utc)
        session.status = "used"
        session.rotated_at = now
        session.access_token = access_token
        session.refresh_token = refresh_token
        await self.redis.set(name=session_key, value=session.model_dump_json(), keepttl=True)

    async def _handle_used_session(self, session:SessionData, payload) -> TokenResponse:
        now = datetime.now(timezone.utc)
        session_deadline = session.rotated_at + timedelta(seconds=15)
        if now > session_deadline:
            await self._revoke_all_sessions(payload.sub)
            raise TokenCompromisedError(user_id=payload.sub, jti=payload.jti)

        if not session.access_token or not session.refresh_token:
            raise InvalidTokenError

        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token
        )

    async def _build_auth_result(self, user: User) -> AuthResult:
        access_token = create_access_token(user.id)
        refresh_token, jti = create_refresh_token(user.id)
        await self._create_session(user.id, jti)

        return AuthResult(
            user=user,
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def register(self, user_in: UserCreate) -> AuthResult:
        if await self.user_repo.get_by_username(user_in.username):
            raise UserAlreadyExistsError

        if await self.user_repo.get_by_email(user_in.email):
            raise UserEmailAlreadyExistsError

        hashed_password = hash_password(user_in.password)
        new_user = User(
            username=user_in.username,
            email=user_in.email,
            hashed_password=hashed_password,
        )
        created_user = await self.user_repo.create(new_user)
        return await self._build_auth_result(created_user)

    async def login(self, user_in: UserLogin) -> AuthResult:
        user = await self.user_repo.get_by_username(user_in.username)
        if not user or not verify_password(user_in.password,user.hashed_password):
            raise InvalidCredentialsError

        return await self._build_auth_result(user)

    async def refresh(self, refresh_token: str) -> TokenResponse:
        payload = self._parse_token(refresh_token)
        if payload.type != "refresh" or not payload.jti:
            raise InvalidTokenError

        session = await self._get_session_by_jti(jti=payload.jti)
        if not session:
            raise InvalidTokenError

        if session.status == "used":
            return await self._handle_used_session(session, payload)

        user = await self.user_repo.get_by_id(payload.sub)
        if not user:
            raise InvalidTokenError

        new_access_token = create_access_token(user.id)
        new_refresh_token, new_jti = create_refresh_token(user.id)

        await self._create_session(user.id, new_jti)
        await self._mark_session_used(
            session,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

    async def get_user_by_token(self, access_token: str) -> User:
        payload = self._parse_token(access_token)
        if payload.type != "access":
            raise InvalidTokenError

        user = await self.user_repo.get_by_id(payload.sub)
        if not user:
            raise InvalidTokenError
        return user

    async def logout(self, refresh_token: str) -> None:
        payload = self._parse_token(refresh_token)
        if payload.type != "refresh" or not payload.jti:
            raise InvalidTokenError

        await self._delete_session(payload.sub, payload.jti)
