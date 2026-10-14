"""Главная: показатели по найму. Роли с изоляцией филиалов видят только свой филиал."""
from datetime import timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import ALL_BRANCHES, Perm, Role
from app.models import Candidate, User, Vacancy, utcnow
from app.schemas.dashboard import DashboardOut
from app.services.dashboard import build_summary
from app.services.vacancy import VacancyStatus

router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])

NEW_PERIOD = timedelta(days=7)


@router.get("/summary", response_model=DashboardOut)
async def summary(
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> dict:
    cand_where = []
    vac_where = [Vacancy.status == VacancyStatus.OPEN.value]
    if Role(user.role) not in ALL_BRANCHES:
        if user.branch_id is None:
            return build_summary({}, 0, 0)
        cand_where.append(Candidate.branch_id == user.branch_id)
        vac_where.append(Vacancy.branch_id == user.branch_id)

    rows = await db.execute(select(Candidate.stage, func.count()).where(*cand_where).group_by(Candidate.stage))
    stage_counts = {stage: n for stage, n in rows.all()}
    since = utcnow() - NEW_PERIOD
    new_week = await db.scalar(select(func.count()).select_from(Candidate).where(*cand_where, Candidate.created_at >= since))
    open_vacancies = await db.scalar(select(func.count()).select_from(Vacancy).where(*vac_where))
    return build_summary(stage_counts, new_week or 0, open_vacancies or 0)
