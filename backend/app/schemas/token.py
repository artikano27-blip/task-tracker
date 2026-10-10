import datetime
from uuid import UUID

from pydantic import BaseModel



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
    status: str = "active"
    rotated_at: datetime.datetime | None = None

class TokenPayload(BaseModel):
    sub: UUID
    type: str
    jti: str | None = None