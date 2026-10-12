from unittest.mock import AsyncMock

import pytest
from app.core.exceptions import TokenCompromisedError
from schemas.token import TokenResponse


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
    assert status["message"] == "Ошибка сервиса аутентификации: Сеанс истек или стал недействительным. Пожалуйста, войдите в систему снова."
    auth_service.refresh.assert_awaited_once_with("compromised_token")
