import uuid
from dataclasses import dataclass

from core.exceptions import UserAlreadyExistsError, UserEmailAlreadyExistsError, \
    InvalidCredentialsError, InvalidTokenError
from core.security import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from models import User
from repositories.user_repository import UserRepository
from schemas import UserCreate
from schemas.token import TokenResponse
from schemas.user import UserLogin


@dataclass
class AuthResult:
    user: User
    access_token: str
    refresh_token: str

class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

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
        access_token = create_access_token(created_user.id)
        refresh_token = create_refresh_token(created_user.id)

        return AuthResult(
            created_user,
            access_token,
            refresh_token
        )

    async def login(self, user_in: UserLogin) -> AuthResult:
        user = await self.user_repo.get_by_username(user_in.username)
        if not user or not verify_password(user_in.password,user.hashed_password):
            raise InvalidCredentialsError

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return AuthResult(
            user,
            access_token,
            refresh_token
        )

    async def refresh(self, refresh_token: str) -> TokenResponse:
        user = await self.get_user_by_token(refresh_token,expected_type="refresh")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    async def get_user_by_token(self, token: str, expected_type: str = "access") -> User:
        payload = decode_token(token)

        if payload.get("type") != expected_type:
            raise InvalidTokenError

        user_id_raw = payload.get("sub")
        try:
            if not user_id_raw:
                raise InvalidTokenError
            user_id = uuid.UUID(user_id_raw)
        except (ValueError, TypeError):
            raise InvalidTokenError

        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise InvalidTokenError

        return user
