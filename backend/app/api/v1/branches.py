from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require
from backend.app.core.database import get_session
from backend.app.core.permissions import Perm
from backend.app.models import Branch, User
from backend.app.schemas.branches import BranchIn, BranchOut
from backend.app.services import branches

router = APIRouter(prefix="/branches", tags=["branches"])


@router.get("", response_model=list[BranchOut])
async def list_branches(
    user: User = Depends(require(Perm.READ)), db: AsyncSession = Depends(get_session)
) -> list[Branch]:
    return await branches.list_for_user(db, user)


@router.post("", response_model=BranchOut, status_code=201)
async def create_branch(
    body: BranchIn,
    user: User = Depends(require(Perm.MANAGE_BRANCHES)),
    db: AsyncSession = Depends(get_session),
) -> Branch:
    return await branches.create(db, user, body)
