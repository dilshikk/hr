from datetime import datetime
from typing import Literal

from pydantic import AwareDatetime, BaseModel, Field

from app.services.scheduling import MAX_DURATION_MIN, MAX_SCORE, MIN_SCORE


class ScheduleIn(BaseModel):
    candidate_id: int
    interviewer_id: int
    # Только со временем и часовым поясом: «голое» время без пояса однозначно не понять.
    starts_at: AwareDatetime
    duration_min: int = Field(30, ge=15, le=MAX_DURATION_MIN)
    format: Literal["offline", "online"] = "offline"


class ScoreIn(BaseModel):
    score: int = Field(ge=MIN_SCORE, le=MAX_SCORE)
    comment: str = Field("", max_length=500)


class ScheduleOut(BaseModel):
    id: int
    candidate_id: int
    candidate_name: str
    interviewer_id: int
    interviewer_name: str
    starts_at: datetime
    duration_min: int
    format: str
    status: str
    score: int | None
    comment: str
