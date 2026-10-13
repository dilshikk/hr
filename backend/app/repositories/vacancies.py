from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Vacancy


async def list_visible(db: AsyncSession, branch_id: int | None, limit: int, offset: int) -> list[Vacancy]:
    """branch_id=None — все филиалы."""
    q = select(Vacancy).order_by(Vacancy.id.desc()).limit(limit).offset(offset)
    if branch_id is not None:
        q = q.where(Vacancy.branch_id == branch_id)
    return list((await db.scalars(q)).all())


async def add(db: AsyncSession, vacancy: Vacancy) -> Vacancy:
    db.add(vacancy)
    await db.flush()
    return vacancy
