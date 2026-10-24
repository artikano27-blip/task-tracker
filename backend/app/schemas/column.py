
import uuid
from pydantic import BaseModel, ConfigDict

from app.schemas import TaskResponse
from app.schemas.user import UserShortResponse


class ColumnCreate(BaseModel):
    title: str

class ColumnUpdate(BaseModel):
    title: str | None = None
    position: int | None = None

class ColumnResponse(BaseModel):
    id: uuid.UUID
    title: str
    tasks: list[TaskResponse]=[]
    user_id: uuid.UUID
    position: int

    model_config = ConfigDict(from_attributes=True)