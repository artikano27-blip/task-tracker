
from typing import Annotated, TypeVar, Type
from fastapi.params import Depends, Cookie
from fastapi.security import APIKeyCookie

from app.use_cases.create_column import CreateColumnCase
from app.use_cases.delete_column import DeleteColumnCase
from app.use_cases.get_columns import GetColumnsCase
from app.use_cases.move_column import MoveColumnCase
from app.use_cases.update_column import UpdateColumnCase
from redis import Redis
from starlette.requests import Request
from app.core.exceptions import UnsupportedMediaTypeError, InvalidTokenError
from app.core.redis import get_redis
from app.core.unit_of_work import SqlAlchemyUnitOfWork
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.use_cases.auth_helpers import parse_token
from app.use_cases.create_task import CreateTaskCase
from app.use_cases.delete_task import DeleteTaskCase
from app.use_cases.get_task import GetTaskCase
from app.use_cases.get_tasks import GetTasksCase
from app.use_cases.login_user import LoginCase
from app.use_cases.logout_user import LogoutCase
from app.use_cases.move_task import MoveTaskCase
from app.use_cases.refresh_token import RefreshTokenCase
from app.use_cases.register_user import RegisterCase
from app.core.database import async_session_maker
from app.use_cases.update_task import UpdateTaskCase

cookie_scheme = APIKeyCookie(name="access_token", auto_error=False)

def get_session_repo(
    redis: Annotated[Redis, Depends(get_redis)]
) -> SessionRepository:
    return SessionRepository(redis)

def get_uow() -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(async_session_maker)

T = TypeVar("T")
def use_case(case_cls: Type[T]):
    def dependency(uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)]) -> T:
        return case_cls(uow)
    return dependency

def get_register_user_use_case(
        uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)],
        session_repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> RegisterCase:
    return RegisterCase(uow, session_repo)


def get_refresh_token_use_case(
        uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)],
        session_repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> RefreshTokenCase:
    return RefreshTokenCase(uow, session_repo)

def get_login_user_use_case(
        uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)],
        session_repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> LoginCase:
    return LoginCase(uow, session_repo)

def get_logout_user_use_case(
        session_repo: Annotated[SessionRepository, Depends(get_session_repo)]
) -> LogoutCase:
    return LogoutCase(session_repo)

get_create_task_use_case = use_case(CreateTaskCase)
get_move_task_use_case=use_case(MoveTaskCase)
get_delete_task_use_case = use_case(DeleteTaskCase)
get_update_task_use_case = use_case(UpdateTaskCase)
get_task_use_case = use_case(GetTaskCase)
get_tasks_use_case = use_case(GetTasksCase)
get_create_column_use_case = use_case(CreateColumnCase)
get_columns_use_case = use_case(GetColumnsCase)
get_update_column_use_case = use_case(UpdateColumnCase)
get_delete_column_use_case = use_case(DeleteColumnCase)
get_move_column_use_case=use_case(MoveColumnCase)



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
    uow: Annotated[SqlAlchemyUnitOfWork, Depends(get_uow)],
    access_token: Annotated[str | None, Depends(cookie_scheme)],
) -> User:
    if not access_token:
        raise InvalidTokenError

    payload = parse_token(access_token)
    if payload.type != "access" or not payload.sub:
        raise InvalidTokenError

    async with uow:
        user = await uow.users.get_by_id(payload.sub)
        if not user:
            raise InvalidTokenError
        return user

async def get_refresh_token(
        refresh_token: Annotated[str | None, Cookie()] = None
) -> str:
    if not refresh_token:
        raise InvalidTokenError
    return refresh_token