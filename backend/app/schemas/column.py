
import uuid
from pydantic import BaseModel, ConfigDict

from app.models import TaskStatus
from app.schemas import TaskResponse
from app.schemas.user import UserShortResponse


class ColumnCreate(BaseModel):
    title: str

class ColumnResponse(BaseModel):
    id: uuid.UUID
    title: str
    tasks: list[TaskResponse]=[]
    user_id: uuid.UUID
    position: int

    model_config = ConfigDict(from_attributes=True)