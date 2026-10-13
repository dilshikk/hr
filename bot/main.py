import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.handlers import router
from config import get_settings


async def main() -> None:
    s = get_settings()
    logging.basicConfig(level=s.log_level)
    if not s.bot_token:
        raise SystemExit("BOT_TOKEN не задан")
    bot = Bot(s.bot_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
