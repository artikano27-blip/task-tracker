import datetime
import uuid
from dataclasses import dataclass, field

from pydantic import BaseModel, ConfigDict, Field


class TaskBase(BaseModel):
    label_text: str
    main_text: str = ""

class TaskCreate(TaskBase):
    column_id : uuid.UUID

class TaskUpdate(BaseModel):
    label_text: str | None = None
    main_text: str | None = None
    column_id: uuid.UUID | None = None
    position: int | None = None
    is_completed: bool | None = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    timestamp: datetime.datetime
    author_id: uuid.UUID
    column_id: uuid.UUID
    position: int
    is_completed: bool
    model_config = ConfigDict(from_attributes=True)

class TaskMove(BaseModel):
    target_column_id: uuid.UUID
    new_position: int = Field(ge=0)

@dataclass
class DailyTaskReport:
    created: list[str] = field(default_factory=list)
    updated: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)