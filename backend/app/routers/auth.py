from typing import Annotated
from fastapi import APIRouter, Response
from fastapi.params import Depends

from app.core.cookie import set_auth_cookies, delete_auth_cookies
from app.core.dependencies import get_body, get_current_user, get_refresh_token, \
    get_register_user_use_case, get_refresh_token_use_case, get_login_user_use_case, get_logout_user_use_case
from app.core.openapi_helpers import dual_body_openapi
from app.models import User
from app.schemas import UserCreate, UserResponse
from app.schemas.user import UserLogin
from app.use_cases.login_user import LoginCase
from app.use_cases.logout_user import LogoutCase
from app.use_cases.refresh_token import RefreshTokenCase
from app.use_cases.register_user import RegisterCase

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/user", response_model=UserResponse, status_code=200, openapi_extra=dual_body_openapi(UserCreate))
async def register_user(
        user_in: Annotated[UserCreate, Depends(get_body(UserCreate))],
        response: Response,
        register_case: Annotated[RegisterCase, Depends(get_register_user_use_case)],
):
    auth_result = await register_case.execute(user_in)
    set_auth_cookies(response, auth_result.access_token, auth_result.refresh_token)
    return auth_result.user


@router.post("/refresh", status_code=200)
async def refresh_token(
        token_in: Annotated[str, Depends(get_refresh_token)],
        response: Response,
        refresh_token_case:Annotated[RefreshTokenCase, Depends(get_refresh_token_use_case)]
):
    tokens = await refresh_token_case.execute(token_in)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return {"ok": True}


@router.post("/session", response_model=UserResponse, status_code=200, openapi_extra=dual_body_openapi(UserLogin))
async def login_user(
        user_in: Annotated[UserLogin, Depends(get_body(UserLogin))],
        response: Response,
        login_case:Annotated[LoginCase, Depends(get_login_user_use_case)]
):
    auth_result = await login_case.execute(user_in)
    set_auth_cookies(response, auth_result.access_token, auth_result.refresh_token)
    return auth_result.user


@router.get("/user", response_model=UserResponse)
async def get_user_profile(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user


@router.delete("/session", status_code=204)
async def logout_user(
        token_in: Annotated[str, Depends(get_refresh_token)],
        response: Response,
        logout_case: Annotated[LogoutCase, Depends(get_logout_user_use_case)]
):
    await logout_case.execute(token_in)
    delete_auth_cookies(response)


