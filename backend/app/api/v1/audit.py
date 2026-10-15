"""Журнал действий. Только чтение, доступ по праву READ_AUDIT (Owner и HR Admin)."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import Perm
from app.models import AuditLog, User
from app.schemas.audit import AuditOut

router = APIRouter(prefix="/api/v1/audit", tags=["audit"])


@router.get("", response_model=list[AuditOut])
async def list_audit(
    action: str | None = Query(None, max_length=64),
    actor_id: int | None = Query(None, ge=1),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(require(Perm.READ_AUDIT)),
    db: AsyncSession = Depends(get_session),
) -> list[AuditOut]:
    # Новые записи первыми; фильтры применяются в запросе, до пагинации.
    q = select(AuditLog, User.full_name).outerjoin(User, User.id == AuditLog.actor_id)
    if action:
        q = q.where(AuditLog.action == action)
    if actor_id:
        q = q.where(AuditLog.actor_id == actor_id)
    q = q.order_by(AuditLog.id.desc()).limit(limit).offset(offset)
    rows = (await db.execute(q)).all()
    return [
        AuditOut(
            id=log.id,
            actor_id=log.actor_id,
            actor_name=name,
            action=log.action,
            target=log.target,
            created_at=log.created_at,
        )
        for log, name in rows
    ]
