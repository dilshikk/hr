"""Интервью кандидата в боте: /interview, затем ответы обычными сообщениями."""
from aiogram import Router
from aiogram.filters import Command, Filter
from aiogram.types import Message

from app.core.database import SessionLocal
from app.services.interview import (
    apply_answer,
    ensure_bot_user,
    get_active,
    is_user_blocked,
    next_question,
    start_interview,
)

router = Router()

DONE_TEXT = {"ru": "Спасибо! Интервью завершено. Мы свяжемся с вами.",
             "uz": "Rahmat! Intervyu yakunlandi. Tez orada siz bilan bog'lanamiz."}
BLOCKED_TEXT = {"ru": "К сожалению, сейчас вы не можете пройти интервью.",
                "uz": "Afsuski, hozir intervyudan o'ta olmaysiz."}


def detect_lang(code: str | None) -> str:
    return "uz" if code and code.lower().startswith("uz") else "ru"


class HasActiveInterview(Filter):
    """Пропускает обычные текстовые сообщения, только если у человека идёт интервью."""

    async def __call__(self, message: Message) -> bool:
        if not message.text or message.text.startswith("/") or message.from_user is None:
            return False
        async with SessionLocal() as db:
            return await get_active(db, message.from_user.id) is not None


@router.message(Command("interview"))
async def begin(message: Message) -> None:
    if message.from_user is None:
        return
    tg = message.from_user
    lang = detect_lang(tg.language_code)
    async with SessionLocal() as db:
        if await is_user_blocked(db, tg.id):
            await message.answer(BLOCKED_TEXT[lang])
            return
        user = await ensure_bot_user(db, tg.id, tg.username, tg.first_name, lang)
        session = await start_interview(db, user)
        question = next_question(user.lang, session.q_count)
        await db.commit()
    await message.answer(question or DONE_TEXT[lang])


@router.message(HasActiveInterview())
async def answer(message: Message) -> None:
    if message.from_user is None or not message.text:
        return
    async with SessionLocal() as db:
        session = await get_active(db, message.from_user.id)
        if session is None:
            return
        user = await ensure_bot_user(
            db, message.from_user.id, message.from_user.username,
            message.from_user.first_name, detect_lang(message.from_user.language_code),
        )
        following = apply_answer(session, user.lang, message.text)
        await db.commit()
    await message.answer(following or DONE_TEXT[user.lang])
