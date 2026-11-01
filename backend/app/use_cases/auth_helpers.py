
from pydantic import ValidationError
from app.core.exceptions import InvalidTokenError
from app.core.security import create_access_token, create_refresh_token, decode_token
from app.models import User
from app.repositories.session_repository import SessionRepository
from app.schemas.token import TokenPayload, AuthResult


async def build_auth_result(
        user: User,
        session_repo: SessionRepository
) -> AuthResult:
    access_token = create_access_token(user.id)
    refresh_token, jti = create_refresh_token(user.id)
    await session_repo.create_session(user.id, jti)

    return AuthResult(
        user=user,
        access_token=access_token,
        refresh_token=refresh_token,
    )


def parse_token(token: str) -> TokenPayload:
    raw_payload = decode_token(token)
    try:
        return TokenPayload.model_validate(raw_payload)
    except ValidationError:
        raise InvalidTokenError


