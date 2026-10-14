from typing import Any

from pydantic import BaseModel


class InterviewListItem(BaseModel):
    id: int
    user_id: int
    name: str
    status: str
    q_count: int


class InterviewOut(BaseModel):
    id: int
    user_id: int
    name: str
    status: str
    q_count: int
    qa_log: list[dict[str, Any]]
    report_resume: Any | None = None
    report_skills: Any | None = None
    report_personality: Any | None = None
