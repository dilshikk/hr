from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.permissions import has_all_branches
from backend.app.models import Branch, User
from backend.app.repositories import audit, branches
from backend.app.schemas.branches import BranchIn


async def list_for_user(db: AsyncSession, user: User) -> list[Branch]:
    if has_all_branches(user.role):
        return await branches.list_visible(db, None)
    if user.branch_id is None:
        return []
    return await branches.list_visible(db, user.branch_id)


async def create(db: AsyncSession, user: User, data: BranchIn) -> Branch:
    branch = await branches.add(db, Branch(name=data.name.strip()))
    audit.log(db, user.id, "branch.create", str(branch.id))
    await db.commit()
    return branch
