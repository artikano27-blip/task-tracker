import datetime
import uuid

from pydantic import BaseModel, ConfigDict, Field
from app.schemas.user import UserShortResponse


class TaskBase(BaseModel):
    label_text: str
    main_text: str

class TaskCreate(TaskBase):
    column_id : uuid.UUID

class TaskUpdate(BaseModel):
    label_text: str | None = None
    main_text: str | None = None
    column_id: uuid.UUID | None = None
    position: int | None = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    timestamp: datetime.datetime
    author: UserShortResponse
    column_id: uuid.UUID
    position: int
    model_config = ConfigDict(from_attributes=True)

class TaskMove(BaseModel):
    target_column_id: uuid.UUID
    new_position: int = Field(ge=0)