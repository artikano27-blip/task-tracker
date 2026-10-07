from typing import Annotated
from fastapi import APIRouter, Response
from fastapi.params import Depends
from core.dependencies import get_auth_service, get_body, get_current_user
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
    response.set_cookie(
        key="refresh_token",
        value=auth_result.refresh_token,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        key="access_token",
        value=auth_result.access_token,
        httponly=True,
        samesite="lax",
    )
    return auth_result.user


@router.post("/refresh", response_model=TokenResponse, status_code=200)
async def refresh_token(
        token_in: RefreshTokenRequest,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    return await auth_service.refresh(token_in.refresh_token)


@router.post("/session", response_model=UserResponse, status_code=200)
async def login_user(
        user_in: Annotated[UserLogin, Depends(get_body(UserLogin))],
        response: Response,
        auth_service: Annotated[AuthService, Depends(get_auth_service)],
):
    auth_result = await auth_service.login(user_in)
    response.set_cookie(
        key="refresh_token",
        value=auth_result.refresh_token,
        httponly=True,
        samesite="lax",
    )
    response.set_cookie(
        key="access_token",
        value=auth_result.access_token,
        httponly=True,
        samesite="lax",
    )
    return auth_result.user

@router.get("/user", response_model=UserResponse)
async def get_user_profile(
        current_user: Annotated[User, Depends(get_current_user)]
):
    return current_user

