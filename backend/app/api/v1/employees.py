"""Сотрудники: назначение ролей и филиалов, блокировка."""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import Perm, can_manage_user
from app.models import AuditLog, AuthSession, Branch, User
from app.schemas.employee import EmployeeOut, EmployeeUpdate

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])


@router.get("", response_model=list[EmployeeOut])
async def list_employees(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(require(Perm.MANAGE_USERS)),
    db: AsyncSession = Depends(get_session),
) -> list[User]:
    q = select(User).order_by(User.id).limit(limit).offset(offset)
    return list((await db.scalars(q)).all())


@router.patch("/{user_id}", response_model=EmployeeOut)
async def update_employee(
    user_id: int,
    body: EmployeeUpdate,
    actor: User = Depends(require(Perm.MANAGE_USERS)),
    db: AsyncSession = Depends(get_session),
) -> User:
    target = await db.get(User, user_id)
    if not target:
        raise HTTPException(404, "Сотрудник не найден")
    new_role = body.role.value if body.role else None
    if not can_manage_user(actor.role, actor.id, target.id, target.role, new_role):
        raise HTTPException(403, "Нельзя изменить этого сотрудника")

    changes: list[str] = []
    if new_role and new_role != target.role:
        changes.append(f"role:{target.role}->{new_role}")
        target.role = new_role
    if body.branch_id is not None:
        branch_id = body.branch_id or None
        if branch_id is not None and not await db.get(Branch, branch_id):
            raise HTTPException(400, "Филиал не найден")
        if branch_id != target.branch_id:
            changes.append(f"branch:{target.branch_id}->{branch_id}")
            target.branch_id = branch_id
    if body.is_active is not None and body.is_active != target.is_active:
        changes.append(f"active:{target.is_active}->{body.is_active}")
        target.is_active = body.is_active

    if changes:
        # Права изменились — старые сессии отзываем, чтобы новые права применились сразу.
        await db.execute(update(AuthSession).where(AuthSession.user_id == target.id).values(revoked=True))
        db.add(AuditLog(actor_id=actor.id, action="employee.update", target=f"{target.id} {';'.join(changes)}"[:64]))
    await db.commit()
    return target
