from app.core.exceptions import InvalidCredentialsError, MaxSessionsReachedError
from app.core.security import verify_password
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.repositories.session_repository import SessionRepository
from app.schemas.token import AuthResult
from app.schemas.user import UserLogin
from app.use_cases.auth_helpers import build_auth_result
from app.core.config import settings


class LoginCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork, session_repo: SessionRepository):
        self.unit = unit
        self.session_repo = session_repo

    async def execute(self, user_in: UserLogin) -> AuthResult:
        async with self.unit:
            user = await self.unit.users.get_by_username(user_in.username)
            if not user or not verify_password(user_in.password, user.hashed_password):
                raise InvalidCredentialsError

        if await self.session_repo.get_sessions_count(user.id) >= settings.MAX_SESSIONS_COUNT:
            raise MaxSessionsReachedError
        return await build_auth_result(user, self.session_repo)
