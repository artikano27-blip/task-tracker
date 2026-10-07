import uuid
from typing import Annotated

from fastapi.params import Depends, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from core.database import get_db
from core.exceptions import UnsupportedMediaTypeError, InvalidTokenError
from core.security import decode_token
from models import User
from repositories.user_repository import UserRepository
from schemas import UserCreate
from services.auth_service import AuthService


async def get_auth_service(
        db: Annotated[AsyncSession, Depends(get_db)],
) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo)


def get_body(schema):
    async def dependency(request: Request):
        content_type = request.headers.get("content-type", "")
        if "application/json" in content_type:
            raw_data = await request.json()
        elif "application/x-www-form-urlencoded" in content_type:
            raw_data = dict(await request.form())
        else:
            raise UnsupportedMediaTypeError
        return schema(**raw_data)

    return dependency


async def get_current_user(
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    if not access_token:
        raise InvalidTokenError
    return await auth_service.get_user_by_token(access_token, expected_type="access")
