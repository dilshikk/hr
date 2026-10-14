"""Уведомления сотрудникам в Telegram о событиях по кандидатам.

Получатели определяются по тем же правилам, что и доступ к данным:
- Owner и HR Admin видят все филиалы, поэтому получают всё;
- рекрутеры и управляющие - только события своего филиала;
- viewer не получает ничего;
- автор действия сообщение о собственном действии не получает.
"""
import logging
from collections.abc import Iterable

from aiogram import Bot
from sqlalchemy import select

from app.core.config import get_settings
from app.core.database import SessionLocal
from app.core.permissions import ALL_BRANCHES, Role
from app.models import User

log = logging.getLogger(__name__)

NOTIFIED_BRANCH_ROLES = {Role.RECRUITER, Role.BRANCH_MANAGER}

STAGE_LABELS_RU: dict[str, str] = {
    "new": "Новый", "review": "Рассмотрение", "contact": "Связались",
    "interview": "Собеседование", "trial": "Стажировка", "offer": "Оффер",
    "hired": "Принят", "rejected": "Отказ", "reserve": "Резерв",
}


def select_recipients(users: Iterable[User], branch_id: int, exclude_user_id: int | None) -> list[User]:
    """Кому слать: активные сотрудники с нужной ролью и доступом к филиалу, кроме автора."""
    result: list[User] = []
    for user in users:
        if not user.is_active or user.id == exclude_user_id:
            continue
        try:
            role = Role(user.role)
        except ValueError:
            continue  # неизвестная роль - без прав, значит и без уведомлений
        if role in ALL_BRANCHES or (role in NOTIFIED_BRANCH_ROLES and user.branch_id == branch_id):
            result.append(user)
    return result


def new_candidate_text(full_name: str) -> str:
    return f"Новый кандидат: {full_name}"


def stage_changed_text(full_name: str, from_stage: str, to_stage: str, reason: str = "") -> str:
    old = STAGE_LABELS_RU.get(from_stage, from_stage)
    new = STAGE_LABELS_RU.get(to_stage, to_stage)
    text = f"{full_name}: {old} -> {new}"
    return f"{text}\nПричина: {reason}" if reason else text


async def notify_branch(branch_id: int, text: str, exclude_user_id: int | None = None) -> int:
    """Отправляет текст сотрудникам филиала. Возвращает число доставленных.

    Вызывается после сохранения данных, поэтому любые ошибки только логируются:
    недоступный Telegram не должен ломать работу с кандидатами.
    """
    token = get_settings().bot_token
    if not token:
        return 0
    try:
        async with SessionLocal() as db:
            users = (await db.scalars(select(User).where(User.is_active.is_(True)))).all()
        recipients = select_recipients(users, branch_id, exclude_user_id)
    except Exception:
        log.exception("Не удалось определить получателей уведомления")
        return 0

    sent = 0
    bot = Bot(token)
    try:
        for user in recipients:
            try:
                await bot.send_message(user.telegram_id, text)
                sent += 1
            except Exception:
                # Например, сотрудник заблокировал бота: остальным всё равно отправляем.
                log.warning("Уведомление сотруднику %s не доставлено", user.id, exc_info=True)
    finally:
        await bot.session.close()
    return sent
