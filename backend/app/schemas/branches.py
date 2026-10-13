from pydantic import BaseModel, Field


class BranchIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class BranchOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
