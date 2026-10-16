import uuid
from datetime import datetime, timezone
from unittest.mock import AsyncMock

import pytest
from app.core.exceptions import TokenCompromisedError
from models import User
from schemas import UserCreate
from schemas.token import TokenResponse
from schemas.user import UserLogin
from services.auth_service import AuthResult


@pytest.mark.asyncio
async def test_refresh_endpoint_success(
        client, auth_service, override_auth_service
):
    # 1. Arrange ⚙️
    fake_tokens = TokenResponse(
        access_token="new-access-token",
        refresh_token="new-refresh-token",
    )
    auth_service.refresh = AsyncMock(return_value=fake_tokens)

    # 2. Act 🌐
    client.cookies.set("refresh_token", "valid_test_token")
    response = await client.post("/auth/refresh")

    # 3. Assert 🔍
    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert response.cookies.get("access_token") == "new-access-token"
    assert response.cookies.get("refresh_token") == "new-refresh-token"
    auth_service.refresh.assert_awaited_once_with("valid_test_token")


@pytest.mark.asyncio
async def test_refresh_endpoint_missing_token_error(client, auth_service, override_auth_service):
    # 2. Act 🌐
    response = await client.post("/auth/refresh")

    assert response.status_code == 401
    status = response.json()
    assert status["message"] == "Ошибка сервиса аутентификации: неверный токен"


@pytest.mark.asyncio
async def test_refresh_endpoint_compromised_token_error(client, auth_service, override_auth_service):
    # 1. Arrange ⚙️
    auth_service.refresh = AsyncMock(side_effect=TokenCompromisedError)
    # 2. Act 🌐
    client.cookies.set("refresh_token", "compromised_token")
    response = await client.post("/auth/refresh")
    # 3. Assert 🔍
    assert response.status_code == 401
    status = response.json()
    assert status[
               "message"] == "Ошибка сервиса аутентификации: Сеанс истек или стал недействительным. Пожалуйста, войдите в систему снова."
    auth_service.refresh.assert_awaited_once_with("compromised_token")


@pytest.mark.asyncio
async def test_create_user_endpoint_success(client, auth_service, override_auth_service):
    # 1. Arrange ⚙️
    fake_user_data = UserCreate(
        username="fake_user",
        email="goddamn27@gmail.com",
        password="just_pass"
    )

    created_user = User(
        id=uuid.uuid4(),
        username="fake_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc)
    )

    fake_auth_result = AuthResult(
        user=created_user,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
    )
    auth_service.register = AsyncMock(return_value=fake_auth_result)

    # 2. Act 🌐
    response = await client.post("/auth/user", json=fake_user_data.model_dump())

    # 3. Assert 🔍
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert response.cookies["access_token"] == "fake-access-token"
    data = response.json()
    assert data["username"] == fake_user_data.username
    assert data["email"] == fake_user_data.email
    assert "password" not in data
    auth_service.register.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_session_endpoint_success(client, auth_service, override_auth_service):
    # 1. Arrange ⚙️
    fake_user_data = UserLogin(
        username="fake_user",
        password="password"
    )

    login_user = User(
        id=uuid.uuid4(),
        username="fake_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc)
    )

    fake_auth_result = AuthResult(
        user=login_user,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
    )
    auth_service.login = AsyncMock(return_value=fake_auth_result)

    # 2. Act 🌐
    response = await client.post("/auth/session", json=fake_user_data.model_dump())

    # 3. Assert 🔍
    assert response.status_code == 200
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    assert response.cookies["access_token"] == "fake-access-token"
    data = response.json()
    assert data["username"] == fake_user_data.username
    assert "password" not in data
    auth_service.login.assert_awaited_once()

@pytest.mark.asyncio
async def test_delete_session_endpoint_success(client, auth_service, override_auth_service):
    # 1. Arrange ⚙️
    auth_service.logout = AsyncMock()

    # 2. Act 🌐
    client.cookies.set("refresh_token", "just_token")
    response = await client.delete("/auth/session")

    # 3. Assert 🔍
    assert response.status_code == 204
    auth_service.logout.assert_awaited_once_with("just_token")
    set_cookies_str = " ".join(response.headers.get_list("set-cookie"))

    assert 'refresh_token=""' in set_cookies_str
    assert "max-age=0" in set_cookies_str.lower()





