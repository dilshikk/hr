from aiogram import Bot

from backend.app.core.config import get_settings


async def notify_admin_chat(bot: Bot, text: str) -> None:
    """Сообщение в служебный чат ADMIN_CHAT_ID (если задан)."""
    chat_id = get_settings().admin_chat_id
    if chat_id:
        await bot.send_message(chat_id, text)
