from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps import require
from api.schemas import VacancyIn, VacancyOut
from db.models import AuditLog, User, Vacancy
from db.session import get_session
from security.rbac import ALL_BRANCHES, Perm, Role, can_access_branch

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
