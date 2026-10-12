import os
os.environ.setdefault("SECRET_KEY", "test-secret-key-3DFSKGDFDFKLNLSDKADSCK['A;s")
import pytest
from unittest.mock import AsyncMock
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from app.core.dependencies import get_auth_service
from main import app


from app.services.auth_service import AuthService


@pytest.fixture
def auth_service():
    mock_user_repo = AsyncMock()
    mock_redis = AsyncMock()
    return AuthService(user_repo=mock_user_repo, redis=mock_redis)

@pytest_asyncio.fixture
async def client():
  transport = ASGITransport(app=app)
  async with AsyncClient(
      transport=transport, base_url="http://test"
  ) as async_client:
    yield async_client

@pytest.fixture
def override_auth_service(auth_service):
    app.dependency_overrides[get_auth_service] = lambda: auth_service
    yield
    app.dependency_overrides.clear()