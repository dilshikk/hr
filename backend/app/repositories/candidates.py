from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import Candidate, PipelineEvent


async def get(db: AsyncSession, candidate_id: int) -> Candidate | None:
    return await db.get(Candidate, candidate_id)


async def list_visible(
    db: AsyncSession, branch_id: int | None, stage: str | None, limit: int, offset: int
) -> list[Candidate]:
    """branch_id=None — все филиалы."""
    q = select(Candidate).order_by(Candidate.id.desc()).limit(limit).offset(offset)
    if branch_id is not None:
        q = q.where(Candidate.branch_id == branch_id)
    if stage:
        q = q.where(Candidate.stage == stage)
    return list((await db.scalars(q)).all())


async def add(db: AsyncSession, candidate: Candidate) -> Candidate:
    db.add(candidate)
    await db.flush()
    return candidate


def add_event(db: AsyncSession, event: PipelineEvent) -> None:
    db.add(event)
