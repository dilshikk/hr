"""Филиалы."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import Perm
from app.models import AuditLog, Branch, User
from app.schemas.employee import BranchIn, BranchOut

router = APIRouter(prefix="/api/v1/branches", tags=["branches"])


@router.get("", response_model=list[BranchOut])
async def list_branches(
    _: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[Branch]:
    return list((await db.scalars(select(Branch).order_by(Branch.name).limit(200))).all())


@router.post("", response_model=BranchOut, status_code=201)
async def create_branch(
    body: BranchIn,
    actor: User = Depends(require(Perm.MANAGE_BRANCHES)),
    db: AsyncSession = Depends(get_session),
) -> Branch:
    name = body.name.strip()
    if await db.scalar(select(Branch).where(Branch.name == name)):
        raise HTTPException(409, "Филиал с таким названием уже есть")
    branch = Branch(name=name)
    db.add(branch)
    await db.flush()
    db.add(AuditLog(actor_id=actor.id, action="branch.create", target=str(branch.id)))
    await db.commit()
    return branch
