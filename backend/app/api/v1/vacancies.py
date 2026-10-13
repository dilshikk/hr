from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import ALL_BRANCHES, Perm, Role, can_access_branch
from app.models import AuditLog, User, Vacancy
from app.schemas.vacancy import VacancyIn, VacancyOut, VacancyStatusIn
from app.services.vacancy import InvalidVacancyStatus, check_vacancy_status

router = APIRouter(prefix="/api/v1/vacancies", tags=["vacancies"])


@router.get("", response_model=list[VacancyOut])
async def list_vacancies(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[Vacancy]:
    q = select(Vacancy).order_by(Vacancy.id.desc()).limit(limit).offset(offset)
    if Role(user.role) not in ALL_BRANCHES:
        if user.branch_id is None:
            return []
        q = q.where(Vacancy.branch_id == user.branch_id)
    return list((await db.scalars(q)).all())


@router.post("", response_model=VacancyOut, status_code=201)
async def create_vacancy(
    body: VacancyIn,
    user: User = Depends(require(Perm.WRITE_VACANCIES)),
    db: AsyncSession = Depends(get_session),
) -> Vacancy:
    if not can_access_branch(user.role, user.branch_id, body.branch_id):
        raise HTTPException(403, "Нет доступа к филиалу")
    vac = Vacancy(**body.model_dump(), owner_id=user.id)
    db.add(vac)
    await db.flush()
    db.add(AuditLog(actor_id=user.id, action="vacancy.create", target=str(vac.id)))
    await db.commit()
    return vac


@router.post("/{vacancy_id}/status", response_model=VacancyOut)
async def set_vacancy_status(
    vacancy_id: int,
    body: VacancyStatusIn,
    user: User = Depends(require(Perm.WRITE_VACANCIES)),
    db: AsyncSession = Depends(get_session),
) -> Vacancy:
    vac = await db.get(Vacancy, vacancy_id)
    if not vac or not can_access_branch(user.role, user.branch_id, vac.branch_id):
        raise HTTPException(404, "Вакансия не найдена")
    old = vac.status
    try:
        vac.status = check_vacancy_status(old, body.status).value
    except InvalidVacancyStatus as exc:
        raise HTTPException(400, str(exc))
    db.add(AuditLog(actor_id=user.id, action="vacancy.status", target=f"{vac.id} {old}->{vac.status}"[:64]))
    await db.commit()
    return vac
