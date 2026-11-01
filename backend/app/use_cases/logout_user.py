
from app.core.exceptions import InvalidTokenError
from app.repositories.session_repository import SessionRepository
from app.use_cases.auth_helpers import parse_token



class LogoutCase:
    def __init__(self, session_repo: SessionRepository):
        self.session_repo = session_repo

    async def execute(self, refresh_token: str) -> None:
        payload = parse_token(refresh_token)
        if payload.type != "refresh" or not payload.jti or not payload.sub:
            raise InvalidTokenError

        await self.session_repo.delete_session(payload.sub, payload.jti)
