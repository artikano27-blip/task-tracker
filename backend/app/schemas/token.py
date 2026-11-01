import datetime
from dataclasses import dataclass
from typing import Literal
from uuid import UUID

from pydantic import BaseModel

from app.models import User


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class SessionData(BaseModel):
    access_token: str | None = None
    refresh_token: str | None = None
    jti: str
    status: Literal["active", "used", "revoked"]
    rotated_at: datetime.datetime | None = None

class TokenPayload(BaseModel):
    sub: UUID
    type: str
    jti: str | None = None

@dataclass
class AuthResult:
    user: User
    access_token: str
    refresh_token: str