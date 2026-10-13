from pydantic import BaseModel, Field

from app.core.permissions import Role


class EmployeeOut(BaseModel):
    id: int
    telegram_id: int
    full_name: str
    role: str
    branch_id: int | None
    is_active: bool

    model_config = {"from_attributes": True}


class EmployeeUpdate(BaseModel):
    """Все поля необязательны: меняется только то, что передано.
    branch_id = 0 означает «снять филиал»."""
    role: Role | None = None
    branch_id: int | None = Field(default=None, ge=0)
    is_active: bool | None = None


class BranchIn(BaseModel):
    name: str = Field(min_length=1, max_length=120)


class BranchOut(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}
