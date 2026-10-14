"""Команды администратора: /staff, /block, /unblock, /stats."""
from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from app.core.database import SessionLocal
from app.models import User
from app.services.staff_admin import (
    StaffError,
    get_actor,
    list_staff,
    set_active,
    stage_stats,
)

router = Router()

NOT_STAFF = "Команда доступна только сотрудникам."


def format_employee(u: User) -> str:
    status = "активен" if u.is_active else "заблокирован"
    branch = f", филиал {u.branch_id}" if u.branch_id else ""
    return f"#{u.id} {u.full_name or '—'} ({u.role}{branch}) — {status}"


def parse_target_id(command: CommandObject) -> int | None:
    arg = (command.args or "").strip()
    return int(arg) if arg.isdigit() else None


@router.message(Command("staff"))
async def staff(message: Message) -> None:
    if message.from_user is None:
        return
    async with SessionLocal() as db:
        actor = await get_actor(db, message.from_user.id)
        if actor is None:
            await message.answer(NOT_STAFF)
            return
        try:
            users = await list_staff(db, actor)
        except StaffError as exc:
            await message.answer(str(exc))
            return
    lines = [format_employee(u) for u in users]
    await message.answer("Сотрудники:\n" + "\n".join(lines) if lines else "Сотрудников нет.")


async def toggle(message: Message, command: CommandObject, active: bool) -> None:
    if message.from_user is None:
        return
    target_id = parse_target_id(command)
    if target_id is None:
        name = "unblock" if active else "block"
        await message.answer(f"Укажите номер сотрудника: /{name} 12")
        return
    async with SessionLocal() as db:
        actor = await get_actor(db, message.from_user.id)
        if actor is None:
            await message.answer(NOT_STAFF)
            return
        try:
            target = await set_active(db, actor, target_id, active)
        except StaffError as exc:
            await message.answer(str(exc))
            return
    await message.answer("Готово: " + format_employee(target))


@router.message(Command("block"))
async def block(message: Message, command: CommandObject) -> None:
    await toggle(message, command, active=False)


@router.message(Command("unblock"))
async def unblock(message: Message, command: CommandObject) -> None:
    await toggle(message, command, active=True)


@router.message(Command("stats"))
async def stats(message: Message) -> None:
    if message.from_user is None:
        return
    async with SessionLocal() as db:
        actor = await get_actor(db, message.from_user.id)
        if actor is None:
            await message.answer(NOT_STAFF)
            return
        try:
            counts = await stage_stats(db, actor)
        except StaffError as exc:
            await message.answer(str(exc))
            return
    if not counts:
        await message.answer("Нет данных: вам не назначен филиал.")
        return
    lines = [f"{stage}: {n}" for stage, n in counts.items()]
    await message.answer("Кандидаты по этапам:\n" + "\n".join(lines))
