"""Фоновая очистка истёкших и отозванных сессий."""
import asyncio
import logging
from datetime import datetime

from sqlalchemy import delete, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import SessionLocal
from app.models import AuthSession, utcnow

log = logging.getLogger(__name__)

CLEANUP_INTERVAL_SECONDS = 3600


async def cleanup_expired_sessions(db: AsyncSession, now: datetime | None = None) -> int:
    """Удаляет сессии с истёкшим сроком или отозванные. Возвращает число удалённых."""
    now = now or utcnow()
    result = await db.execute(
        delete(AuthSession).where(or_(AuthSession.expires_at < now, AuthSession.revoked.is_(True)))
    )
    await db.commit()
    return result.rowcount or 0


async def run_cleanup_loop() -> None:
    """Бесконечный цикл в процессе API. Ошибки логируются и не останавливают цикл."""
    while True:
        try:
            async with SessionLocal() as db:
                removed = await cleanup_expired_sessions(db)
            if removed:
                log.info("Удалено старых сессий: %s", removed)
        except Exception:
            log.exception("Ошибка очистки сессий")
        await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
