from pydantic import BaseModel, Field


class TelegramAuthIn(BaseModel):
    init_data: str = Field(min_length=1, max_length=4096)


class SessionOut(BaseModel):
    token: str
    role: str


class CandidateIn(BaseModel):
    full_name: str = Field(min_length=1, max_length=200)
    phone: str | None = Field(default=None, max_length=32)
    branch_id: int
    vacancy_id: int | None = None


class CandidateOut(BaseModel):
    id: int
    full_name: str
    phone: str | None
    branch_id: int
    vacancy_id: int | None
    stage: str

    model_config = {"from_attributes": True}


class StageIn(BaseModel):
    stage: str
    reason: str = Field(default="", max_length=300)


class VacancyIn(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    branch_id: int
    description: str = Field(default="", max_length=5000)


class VacancyOut(BaseModel):
    id: int
    title: str
    branch_id: int
    status: str

    model_config = {"from_attributes": True}
