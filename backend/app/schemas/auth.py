from pydantic import BaseModel, Field


class TelegramAuthIn(BaseModel):
    init_data: str = Field(min_length=1, max_length=4096)


class SessionOut(BaseModel):
    token: str
    role: str


class MeOut(BaseModel):
    id: int
    name: str
    role: str
    branch_id: int | None
