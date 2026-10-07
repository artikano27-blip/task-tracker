import uuid
from datetime import datetime,timezone,timedelta
import bcrypt
import jwt

from core.config import settings
from core.exceptions import ExpiredTokenError, InvalidTokenError


def create_token(data: dict, token_type: str, expires_delta: timedelta | None = None) -> str:
    if expires_delta is None:
        expires_delta = (
            timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            if token_type == "access"
            else timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_access_token(user_id: uuid.UUID) -> str:
    return create_token(
        data={"sub": str(user_id)},
        token_type="access"
    )

def create_refresh_token(user_id: uuid.UUID) -> str:
    return create_token(
        data={"sub": str(user_id)},
        token_type="refresh"
    )

def hash_password(password: str) -> str:
    pwd_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(pwd_bytes, hashed_bytes)

def decode_token(token:str) -> dict:
    secret_key = settings.SECRET_KEY
    algorithm = settings.ALGORITHM
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
    except jwt.ExpiredSignatureError:
        raise ExpiredTokenError
    except jwt.InvalidTokenError:
        raise InvalidTokenError
    return payload