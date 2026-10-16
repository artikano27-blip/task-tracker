
import uuid
from datetime import timedelta, datetime, timezone
from unittest.mock import MagicMock, AsyncMock, ANY

import pytest

from app.core.exceptions import TokenCompromisedError, InvalidTokenError
from app.core.exceptions import UserAlreadyExistsError, UserEmailAlreadyExistsError, InvalidCredentialsError
from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate
from app.schemas.token import SessionData, TokenPayload
from app.schemas.user import UserLogin
from app.services.auth_service import AuthResult


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

@pytest.mark.asyncio
async def test_register_success(auth_service):
    # Arrange (Подготовка)
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

    auth_service.user_repo.get_by_username = AsyncMock(return_value=None)
    auth_service.user_repo.get_by_email = AsyncMock(return_value=None)
    auth_service.user_repo.create = AsyncMock(return_value=created_user)
    auth_service._build_auth_result = AsyncMock(return_value=fake_auth_result)

    # 2. Act 🌐
    result = await auth_service.register(fake_user_data)

    # Assert (Проверки)
    auth_service.user_repo.create.assert_awaited_once()
    passed_user = auth_service.user_repo.create.call_args[0][0]
    assert passed_user.username == fake_user_data.username
    assert passed_user.email == fake_user_data.email
    assert passed_user.hashed_password != fake_user_data.password
    auth_service._build_auth_result.assert_awaited_once_with(created_user)
    assert result == fake_auth_result

@pytest.mark.asyncio
async def test_register_username_already_exists(auth_service):
    # Arrange (Подготовка)
    fake_user_data = UserCreate(
        username="fake_user",
        email="goddamn27@gmail.com",
        password="just_pass"
    )

    current_user = User(
        id=uuid.uuid4(),
        username="fake_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc)
    )
    auth_service.user_repo.get_by_username = AsyncMock(return_value=current_user)

    # 2. Act 🌐
    with pytest.raises(UserAlreadyExistsError):
        await auth_service.register(fake_user_data)

    auth_service.user_repo.create.assert_not_awaited()

@pytest.mark.asyncio
async def test_register_email_already_exists(auth_service):
    # Arrange (Подготовка)
    fake_user_data = UserCreate(
        username="fake_user",
        email="goddamn27@gmail.com",
        password="just_pass"
    )

    current_user = User(
        id=uuid.uuid4(),
        username="fake_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc)
    )
    auth_service.user_repo.get_by_username = AsyncMock(return_value=None)
    auth_service.user_repo.get_by_email = AsyncMock(return_value=current_user)

    # 2. Act 🌐
    with pytest.raises(UserEmailAlreadyExistsError):
        await auth_service.register(fake_user_data)

    auth_service.user_repo.create.assert_not_awaited()

@pytest.mark.asyncio
async def test_login_success(auth_service):
    # Arrange (Подготовка)
    fake_user_data = UserLogin(
        username="login_user",
        password="qwerty_boy"
    )

    current_user = User(
        id=uuid.uuid4(),
        username="login_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc),
        hashed_password=hash_password(fake_user_data.password)
    )

    fake_auth_result = AuthResult(
        user=current_user,
        access_token="fake-access-token",
        refresh_token="fake-refresh-token",
    )
    auth_service.user_repo.get_by_username = AsyncMock(return_value=current_user)
    auth_service._build_auth_result = AsyncMock(return_value=fake_auth_result)

    # 2. Act 🌐
    result = await auth_service.login(fake_user_data)

    # Assert (Проверки)
    auth_service._build_auth_result.assert_awaited_once_with(current_user)
    assert result == fake_auth_result

@pytest.mark.asyncio
async def test_login_wrong_password(auth_service):
    # Arrange (Подготовка)
    fake_user_data = UserLogin(
        username="login_user",
        password="qwerty_girl"
    )
    current_user = User(
        id=uuid.uuid4(),
        username="login_user",
        email="goddamn27@gmail.com",
        created_at=datetime.now(timezone.utc),
        hashed_password=hash_password("qwerty_boy")
    )
    auth_service.user_repo.get_by_username = AsyncMock(return_value=current_user)
    auth_service._build_auth_result = AsyncMock()

    # 2. Act 🌐
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(fake_user_data)

    # Assert (Проверки)
    auth_service._build_auth_result.assert_not_awaited()

@pytest.mark.asyncio
async def test_login_user_not_found(auth_service):
    # Arrange (Подготовка)
    fake_user_data = UserLogin(
        username="login_user",
        password="qwerty_girl"
    )
    auth_service.user_repo.get_by_username = AsyncMock(return_value = None)
    auth_service._build_auth_result = AsyncMock()

    # 2. Act 🌐
    with pytest.raises(InvalidCredentialsError):
        await auth_service.login(fake_user_data)

    # Assert (Проверки)
    auth_service._build_auth_result.assert_not_awaited()

@pytest.mark.asyncio
async def test_logout_success(auth_service):
    # Arrange (Подготовка)
    test_user_id = uuid.uuid4()

    payload = TokenPayload(sub=test_user_id, jti="just-jti", type="refresh")
    auth_service._parse_token = MagicMock(return_value=payload)
    auth_service._delete_session = AsyncMock()

    # 2. Act 🌐
    result = await auth_service.logout("refresh_token")

    # Assert (Проверки)
    auth_service._delete_session.assert_awaited_once_with(payload.sub,payload.jti)

@pytest.mark.asyncio
async def test_logout_wrong_token_type(auth_service):
    # Arrange (Подготовка)
    test_user_id = uuid.uuid4()

    payload = TokenPayload(sub=test_user_id, jti="just-jti", type="access")
    auth_service._parse_token = MagicMock(return_value=payload)
    auth_service._delete_session = AsyncMock()

    # 2. Act 🌐
    with pytest.raises(InvalidTokenError):
        await auth_service.logout("pretend_to_be_refresh_token")

    # Assert (Проверки)
    auth_service._delete_session.assert_not_awaited()

@pytest.mark.asyncio
async def test_logout_empty_payload_jti(auth_service):
    # Arrange (Подготовка)
    test_user_id = uuid.uuid4()

    payload = TokenPayload(sub=test_user_id, jti="", type="refresh")
    auth_service._parse_token = MagicMock(return_value=payload)
    auth_service._delete_session = AsyncMock()

    # 2. Act 🌐
    with pytest.raises(InvalidTokenError):
        await auth_service.logout("refresh_token")

    # Assert (Проверки)
    auth_service._delete_session.assert_not_awaited()
















