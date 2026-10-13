from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import AuditLog


def log(db: AsyncSession, actor_id: int | None, action: str, target: str = "") -> None:
    db.add(AuditLog(actor_id=actor_id, action=action, target=target))
