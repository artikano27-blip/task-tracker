
import uuid
from datetime import timedelta, datetime, timezone
from unittest.mock import MagicMock, AsyncMock, ANY

import pytest

from app.core.exceptions import TokenCompromisedError
from schemas.token import SessionData, TokenPayload


@pytest.mark.asyncio
async def test_refresh_token_compromised(auth_service):
    test_user_id = uuid.uuid4()
    past_time = datetime.now(timezone.utc) - timedelta(seconds=20)
    session = SessionData(jti="test-jti",rotated_at=past_time, status="used")
    payload = TokenPayload(sub=test_user_id,jti=session.jti,type="refresh")

    auth_service._parse_token = MagicMock(return_value = payload)
    auth_service._get_session_by_jti = AsyncMock(return_value = session)
    auth_service._revoke_all_sessions = AsyncMock()


    with pytest.raises(TokenCompromisedError):
        await auth_service.refresh("abcde245dsf")

    auth_service._revoke_all_sessions.assert_awaited_once_with(test_user_id)

@pytest.mark.asyncio
async def test_refresh_token_grace_period(auth_service):
    # Arrange (Подготовка)
    test_user_id = uuid.uuid4()
    recent_past = datetime.now(timezone.utc) - timedelta(seconds=5)
    session = SessionData(
        jti="tested-by-admin",
        rotated_at=recent_past,
        status="used",
        access_token="existing-access-token",
        refresh_token="existing-refresh-token",
    )
    payload = TokenPayload(sub=test_user_id, jti=session.jti, type="refresh")

    auth_service._parse_token = MagicMock(return_value=payload)
    auth_service._get_session_by_jti = AsyncMock(return_value=session)
    auth_service._revoke_all_sessions = AsyncMock()

    # Act (Вызов)
    result = await auth_service.refresh("abcde245sfg")

    # Assert (Проверки)
    auth_service._revoke_all_sessions.assert_not_awaited()
    assert result.access_token == session.access_token
    assert result.refresh_token == session.refresh_token

@pytest.mark.asyncio
async def test_refresh_token_success(auth_service):
    # Arrange (Подготовка)
    test_user_id = uuid.uuid4()
    session = SessionData(
        jti="tested-by-admin",
        status="active",
        access_token="existing-access-token",
        refresh_token="existing-refresh-token",
    )
    payload = TokenPayload(sub=test_user_id, jti=session.jti, type="refresh")
    fake_user = MagicMock(id=test_user_id)
    auth_service.user_repo.get_by_id = AsyncMock(return_value=fake_user)
    auth_service._parse_token = MagicMock(return_value=payload)
    auth_service._get_session_by_jti = AsyncMock(return_value=session)
    auth_service._create_session = AsyncMock()
    auth_service._mark_session_used = AsyncMock()

    # Act (Вызов)
    result = await auth_service.refresh("abcde245sfg")

    assert result.access_token != session.access_token
    assert result.refresh_token != session.refresh_token
    auth_service._create_session.assert_awaited_once_with(test_user_id, ANY)
    auth_service._mark_session_used.assert_awaited_once_with(session, access_token = result.access_token, refresh_token = result.refresh_token)



