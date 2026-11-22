import uuid
from pydantic import BaseModel, Field


class DailyTaskReport(BaseModel):
    completed: list[str] = Field(default_factory=list)
    created: list[str] = Field(default_factory=list)
    updated: list[str] = Field(default_factory=list)


class SummaryRequest(BaseModel):
    user_id: uuid.UUID
    email: str
    username: str
    tasks: DailyTaskReport


class SummaryResponse(BaseModel):
    user_id: uuid.UUID
    email: str
    username: str
    summary_text: str