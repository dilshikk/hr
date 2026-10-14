import asyncio

from aiogram import Bot, Dispatcher

from app.core.config import get_settings
from app.core.logging import setup_logging
from bot.handlers import admin, interview, notifications, start


async def main() -> None:
    s = get_settings()
    setup_logging()
    if not s.bot_token:
        raise SystemExit("BOT_TOKEN не задан")
    bot = Bot(s.bot_token)
    dp = Dispatcher()
    dp.include_routers(start.router, interview.router, notifications.router, admin.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
