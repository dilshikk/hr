import asyncio
import logging

from aiogram import Bot, Dispatcher

from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from bot.handlers import admin, start


async def main() -> None:
    s = get_settings()
    setup_logging(s.log_level)
    if not s.bot_token:
        raise SystemExit("BOT_TOKEN не задан")
    bot = Bot(s.bot_token)
    dp = Dispatcher()
    dp.include_router(start.router)
    dp.include_router(admin.router)
    logging.getLogger(__name__).info("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
