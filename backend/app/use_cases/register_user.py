from app.core.exceptions import UserAlreadyExistsError, UserEmailAlreadyExistsError
from app.core.security import hash_password
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.schemas import UserCreate
from app.schemas.token import AuthResult
from app.use_cases.auth_helpers import build_auth_result


class RegisterCase:
    def __init__(self, unit: SqlAlchemyUnitOfWork, session_repo: SessionRepository):
        self.unit = unit
        self.session_repo = session_repo

    async def execute(self, user_in: UserCreate) -> AuthResult:
        async with self.unit:
            if await self.unit.users.get_by_username(user_in.username):
                raise UserAlreadyExistsError

            if await self.unit.users.get_by_email(user_in.email):
                raise UserEmailAlreadyExistsError

            hashed_password = hash_password(user_in.password)
            new_user = User(
                username=user_in.username,
                email=user_in.email,
                hashed_password=hashed_password,
            )
            created_user = await self.unit.users.create(new_user)
            await self.unit.columns.create_default_columns(created_user.id)

        auth_result = await build_auth_result(created_user, self.session_repo)
        return auth_result