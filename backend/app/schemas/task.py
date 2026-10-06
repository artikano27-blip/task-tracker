import datetime
import uuid

from pydantic import BaseModel, ConfigDict

from app.models import TaskStatus


class TaskBase(BaseModel):
    label_text: str
    main_text: str

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    label_text: str | None = None
    main_text: str | None = None
    status: TaskStatus | None = None

class TaskResponse(TaskBase):
    id: uuid.UUID
    timestamp: datetime.datetime
    author_id: uuid.UUID
    status: TaskStatus

    model_config = ConfigDict(from_attributes=True)