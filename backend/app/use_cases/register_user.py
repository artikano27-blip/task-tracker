
from app.schemas import UserCreate
from app.services.auth_service import AuthService, AuthResult
from app.services.column_service import ColumnService


class RegisterCase:
    def __init__(self, auth_service: AuthService, column_service: ColumnService):
        self.auth_service = auth_service
        self.column_service = column_service

    async def execute(self, user_in: UserCreate) -> AuthResult:
        auth_result = await self.auth_service.register(user_in)
        await self.column_service.create_default_columns(auth_result.user.id)
        return auth_result