from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from config import get_settings

router = Router()


@router.message(CommandStart())
async def start(message: Message) -> None:
    url = get_settings().webapp_url
    if not url.startswith("https://"):
        await message.answer("Здравствуйте! HR-панель пока не настроена.")
        return
    kb = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="Открыть HR-панель", web_app=WebAppInfo(url=url)),
    ]])
    await message.answer("Здравствуйте! Откройте HR-панель MADO:", reply_markup=kb)
