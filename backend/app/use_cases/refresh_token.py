from datetime import timezone, datetime, timedelta

from app.core.exceptions import InvalidTokenError, TokenCompromisedError, ExpiredTokenError
from app.core.security import create_access_token, create_refresh_token
from app.core.unit_of_work import SqlAlchemyUnitOfWork

from app.repositories.session_repository import SessionRepository
from app.schemas.token import TokenResponse, SessionData
from app.use_cases.auth_helpers import parse_token


class RefreshTokenCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork, session_repo: SessionRepository):
        self.unit = unit
        self.session_repo = session_repo

    async def _handle_used_session(self, session: SessionData, payload) -> TokenResponse:
        now = datetime.now(timezone.utc)
        session_deadline = session.rotated_at + timedelta(seconds=15)
        if now > session_deadline:
            await self.session_repo.revoke_all_sessions(payload.sub)
            raise TokenCompromisedError(user_id=payload.sub, jti=payload.jti)

        if not session.access_token or not session.refresh_token:
            raise InvalidTokenError

        return TokenResponse(
            access_token=session.access_token,
            refresh_token=session.refresh_token
        )

    async def execute(self, refresh_token: str) -> TokenResponse:
        payload = parse_token(refresh_token)
        if payload.type != "refresh" or not payload.jti:
            raise InvalidTokenError

        session = await self.session_repo.get_session_by_jti(jti=payload.jti)
        if not session:
            raise InvalidTokenError

        if session.status == "revoked":
            raise ExpiredTokenError

        if session.status == "used":
            return await self._handle_used_session(session, payload)

        async with self.unit:
            user = await self.unit.users.get_by_id(payload.sub)
            if not user:
                raise InvalidTokenError

        new_access_token = create_access_token(user.id)
        new_refresh_token, new_jti = create_refresh_token(user.id)

        await self.session_repo.rotate_session(
            user_id=user.id,
            old_session=session,
            new_jti=new_jti,
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )

        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
        )
