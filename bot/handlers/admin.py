from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from backend.app.core.config import get_settings

router = Router()


@router.message(Command("whoami"))
async def whoami(message: Message) -> None:
    """Показывает Telegram ID — нужен, чтобы внести его в ADMIN_IDS. Только для админов."""
    uid = message.from_user.id if message.from_user else 0
    if uid not in get_settings().admin_id_set:
        return
    await message.answer(f"Ваш Telegram ID: {uid}")
