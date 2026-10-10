from typing import Annotated
from fastapi import APIRouter, Response
from fastapi.params import Depends

from core.cookie import set_auth_cookies, delete_auth_cookies
from core.dependencies import get_auth_service, get_body, get_current_user, get_refresh_token
from models import User
from schemas import UserCreate, UserResponse
from schemas.token import TokenResponse, RefreshTokenRequest
from schemas.user import UserLogin
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Аутентификация"])


@router.post("/user", response_model=UserResponse, status_code=200)
async def register_user(
        user_in: Annotated[UserCreate, Depends(get_body(UserCreate))],
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    auth_result = await auth_service.register(user_in)
    set_auth_cookies(response, auth_result.access_token, auth_result.refresh_token)
    return auth_result.user


@router.post("/refresh", status_code=200)
async def refresh_token(
        token_in: Annotated[str, Depends(get_refresh_token)],
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        response: Response,
):
    tokens = await auth_service.refresh(token_in)
    set_auth_cookies(response, tokens.access_token, tokens.refresh_token)
    return {"ok": True}


@router.post("/session", response_model=UserResponse, status_code=200)
async def login_user(
        user_in: Annotated[UserLogin, Depends(get_body(UserLogin))],
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    auth_result = await auth_service.login(user_in)
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
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
        response: Response,

):
    await auth_service.logout(token_in)
    delete_auth_cookies(response)


