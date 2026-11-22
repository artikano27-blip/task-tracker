from pydantic import BaseModel


class SummaryResponse(BaseModel):
    email: str
    username: str
    summary_text: str