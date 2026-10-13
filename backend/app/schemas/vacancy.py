from pydantic import BaseModel, Field


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
