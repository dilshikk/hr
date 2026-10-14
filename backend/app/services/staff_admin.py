"""Логика админ-команд бота: список сотрудников, блокировка, статистика по этапам.

Права проверяются так же, как в API: has_perm / can_manage_user / изоляция филиалов.
"""
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.permissions import ALL_BRANCHES, Perm, Role, can_manage_user, has_perm
from app.models import AuditLog, AuthSession, Candidate, User
from app.services.pipeline import Stage

STAFF_LIMIT = 30


class StaffError(Exception):
    """Ошибка с текстом, который можно показать пользователю бота."""


async def get_actor(db: AsyncSession, telegram_id: int) -> User | None:
    """Сотрудник по Telegram ID; заблокированный считается неизвестным."""
    user = await db.scalar(select(User).where(User.telegram_id == telegram_id))
    return user if user and user.is_active else None


async def list_staff(db: AsyncSession, actor: User) -> list[User]:
    if not has_perm(actor.role, Perm.MANAGE_USERS):
        raise StaffError("Недостаточно прав.")
    q = select(User).order_by(User.id).limit(STAFF_LIMIT)
    return list((await db.scalars(q)).all())


async def set_active(db: AsyncSession, actor: User, target_id: int, active: bool) -> User:
    """Блокирует или разблокирует сотрудника по внутреннему ID, отзывает его сессии."""
    if not has_perm(actor.role, Perm.MANAGE_USERS):
        raise StaffError("Недостаточно прав.")
    target = await db.get(User, target_id)
    if target is None:
        raise StaffError("Сотрудник не найден.")
    if not can_manage_user(actor.role, actor.id, target.id, target.role, None):
        raise StaffError("Нельзя изменить этого сотрудника.")
    if target.is_active != active:
        target.is_active = active
        # Права изменились — старые сессии отзываем, чтобы блокировка применилась сразу.
        await db.execute(update(AuthSession).where(AuthSession.user_id == target.id).values(revoked=True))
        db.add(AuditLog(
            actor_id=actor.id,
            action="employee.update",
            target=f"{target.id} active:{not active}->{active}"[:64],
        ))
    await db.commit()
    return target


async def stage_stats(db: AsyncSession, actor: User) -> dict[str, int]:
    """Число кандидатов по этапам. Роли с изоляцией видят только свой филиал."""
    if not has_perm(actor.role, Perm.READ):
        raise StaffError("Недостаточно прав.")
    q = select(Candidate.stage, func.count()).group_by(Candidate.stage)
    if Role(actor.role) not in ALL_BRANCHES:
        if actor.branch_id is None:
            return {}
        q = q.where(Candidate.branch_id == actor.branch_id)
    counts = {stage: n for stage, n in (await db.execute(q)).all()}
    # Порядок воронки, этапы без кандидатов не скрываем.
    return {s.value: counts.get(s.value, 0) for s in Stage}
