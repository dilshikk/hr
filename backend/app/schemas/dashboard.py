from pydantic import BaseModel


class DashboardOut(BaseModel):
    total: int
    new_last_week: int
    in_progress: int
    hired: int
    open_vacancies: int
    by_stage: dict[str, int]
