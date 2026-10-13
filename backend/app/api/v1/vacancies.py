from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require
from backend.app.core.database import get_session
from backend.app.core.permissions import Perm
from backend.app.models import User, Vacancy
from backend.app.schemas.vacancies import VacancyIn, VacancyOut
from backend.app.services import vacancies

router = APIRouter(prefix="/vacancies", tags=["vacancies"])


@router.get("", response_model=list[VacancyOut])
async def list_vacancies(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[Vacancy]:
    return await vacancies.list_for_user(db, user, limit, offset)


@router.post("", response_model=VacancyOut, status_code=201)
async def create_vacancy(
    body: VacancyIn,
    user: User = Depends(require(Perm.WRITE_VACANCIES)),
    db: AsyncSession = Depends(get_session),
) -> Vacancy:
    return await vacancies.create(db, user, body)
