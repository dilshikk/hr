from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from backend.app.core.config import get_settings
from bot.keyboards.main_menu import open_panel_keyboard

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    url = get_settings().webapp_url
    if not url.startswith("https://"):
        await message.answer("Здравствуйте! HR-панель пока не настроена.")
        return
    await message.answer("Здравствуйте! Откройте HR-панель MADO:", reply_markup=open_panel_keyboard(url))
