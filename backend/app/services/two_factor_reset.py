"""Сброс 2FA сотруднику, потерявшему телефон и коды восстановления.

После сброса сотрудник при следующем входе снова настраивает 2FA с нуля.
"""
from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import Role
from app.core.totp import requires_2fa
from app.models import AuditLog, AuthSession, RecoveryCode, User, UserTotp


def can_reset_2fa(actor_role: str, actor_id: int, target_id: int, target_role: str) -> bool:
    """Сбросить может только Owner и только другому сотруднику с обязательной 2FA.

    HR Admin сбросить не может: его цели (Owner/HR Admin) для него запрещены, иначе он
    мог бы отключить защиту у Owner. Себя сбросить нельзя — иначе украденная сессия сняла бы защиту.
    """
    try:
        if Role(actor_role) is not Role.OWNER:
            return False
    except ValueError:
        return False
    return actor_id != target_id and requires_2fa(target_role)


async def reset_two_factor(db: AsyncSession, actor: User, target: User) -> None:
    """Удаляет секрет и коды восстановления, отзывает сессии, пишет в аудит. Коммит - на вызывающем."""
    await db.execute(delete(UserTotp).where(UserTotp.user_id == target.id))
    await db.execute(delete(RecoveryCode).where(RecoveryCode.user_id == target.id))
    # Текущие сессии входили со старым вторым шагом - завершаем их, дальше вход только через новую настройку.
    await db.execute(update(AuthSession).where(AuthSession.user_id == target.id).values(revoked=True))
    db.add(AuditLog(actor_id=actor.id, action="2fa.reset", target=str(target.id)))
