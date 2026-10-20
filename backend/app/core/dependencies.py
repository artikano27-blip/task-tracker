
from typing import Annotated
from fastapi.params import Depends, Cookie
from fastapi.security import APIKeyCookie
from redis import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.core.database import get_db
from app.core.exceptions import UnsupportedMediaTypeError, InvalidTokenError
from app.core.redis import get_redis
from app.models import User
from app.repositories.task_repository import TaskRepository
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.task_service import TaskService

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

async def get_auth_service(
        db: Annotated[AsyncSession, Depends(get_db)],
        redis: Annotated[Redis, Depends(get_redis)]
) -> AuthService:
    user_repo = UserRepository(db)
    return AuthService(user_repo, redis)

async def get_task_service(
        db: Annotated[AsyncSession, Depends(get_db)]
) -> TaskService:
    task_repo = TaskRepository(db)
    return TaskService(task_repo)





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
        access_token: Annotated[str | None, Depends(cookie_scheme)],
) -> User:
    if not access_token:
        raise InvalidTokenError
    return await auth_service.get_user_by_token(access_token)

async def get_refresh_token(
        refresh_token: Annotated[str | None, Cookie()] = None
) -> str:
    if not refresh_token:
        raise InvalidTokenError
    return refresh_token