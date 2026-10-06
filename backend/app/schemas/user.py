import datetime
import uuid

from pydantic import BaseModel, ConfigDict
from pydantic.v1 import EmailStr


class UserBase(BaseModel):
    username: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: uuid.UUID
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)
