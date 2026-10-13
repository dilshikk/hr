from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Branch


async def list_visible(db: AsyncSession, branch_id: int | None) -> list[Branch]:
    """branch_id=None — все филиалы."""
    q = select(Branch).order_by(Branch.name)
    if branch_id is not None:
        q = q.where(Branch.id == branch_id)
    return list((await db.scalars(q)).all())


async def add(db: AsyncSession, branch: Branch) -> Branch:
    db.add(branch)
    await db.flush()
    return branch
