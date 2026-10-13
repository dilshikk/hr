from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.permissions import can_access_branch, has_all_branches
from backend.app.models import User, Vacancy
from backend.app.repositories import audit, vacancies
from backend.app.schemas.vacancies import VacancyIn
from backend.app.services.errors import ServiceError


async def list_for_user(db: AsyncSession, user: User, limit: int, offset: int) -> list[Vacancy]:
    if has_all_branches(user.role):
        return await vacancies.list_visible(db, None, limit, offset)
    if user.branch_id is None:
        return []
    return await vacancies.list_visible(db, user.branch_id, limit, offset)


async def create(db: AsyncSession, user: User, data: VacancyIn) -> Vacancy:
    if not can_access_branch(user.role, user.branch_id, data.branch_id):
        raise ServiceError(403, "Нет доступа к филиалу")
    vac = await vacancies.add(db, Vacancy(**data.model_dump(), owner_id=user.id))
    audit.log(db, user.id, "vacancy.create", str(vac.id))
    await db.commit()
    return vac
