"""Интервью в боте: вопросы, запись ответов, проверка чёрного списка."""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import BlacklistEntry, BotUser, InterviewSession

MAX_ANSWER_LEN = 2000

# Фиксированный список вопросов. Подключить генерацию вопросов через ИИ можно,
# заменив next_question: остальной код от источника вопросов не зависит.
QUESTIONS: dict[str, list[str]] = {
    "ru": [
        "Как вас зовут и сколько вам лет?",
        "На какую должность вы хотите устроиться?",
        "Есть ли у вас опыт работы в общепите? Расскажите кратко.",
        "Почему вы хотите работать в MADO?",
        "Какой график вам подходит и когда вы можете выйти на работу?",
    ],
    "uz": [
        "Ismingiz nima va necha yoshdasiz?",
        "Qaysi lavozimga ishga kirmoqchisiz?",
        "Umumiy ovqatlanish sohasida tajribangiz bormi? Qisqacha aytib bering.",
        "Nima uchun MADO da ishlashni xohlaysiz?",
        "Qaysi ish jadvali sizga mos va qachon ishni boshlay olasiz?",
    ],
}

STATUS_ACTIVE = "active"
STATUS_DONE = "done"


def questions_for(lang: str) -> list[str]:
    return QUESTIONS.get(lang, QUESTIONS["ru"])


def next_question(lang: str, q_count: int) -> str | None:
    """Следующий вопрос по числу уже полученных ответов; None - интервью закончено."""
    questions = questions_for(lang)
    return questions[q_count] if q_count < len(questions) else None


def is_blocked(entry: BlacklistEntry | None, now: datetime | None = None) -> bool:
    """Пустая дата разблокировки - бессрочная блокировка."""
    if entry is None:
        return False
    if entry.unblock_at is None:
        return True
    unblock_at = entry.unblock_at
    if unblock_at.tzinfo is None:
        unblock_at = unblock_at.replace(tzinfo=timezone.utc)
    return unblock_at > (now or datetime.now(timezone.utc))


def apply_answer(session: InterviewSession, lang: str, answer: str) -> str | None:
    """Записывает ответ на текущий вопрос. Возвращает следующий вопрос или None, если конец."""
    question = next_question(lang, session.q_count)
    if question is None:
        session.status = STATUS_DONE
        return None
    # Присваиваем новый список: SQLAlchemy не замечает изменений внутри JSON на месте.
    session.qa_log = [*session.qa_log, {"q": question, "a": answer.strip()[:MAX_ANSWER_LEN]}]
    session.q_count = len(session.qa_log)
    following = next_question(lang, session.q_count)
    if following is None:
        session.status = STATUS_DONE
    return following


async def get_active(db: AsyncSession, user_id: int) -> InterviewSession | None:
    return await db.scalar(
        select(InterviewSession)
        .where(InterviewSession.user_id == user_id, InterviewSession.status == STATUS_ACTIVE)
        .order_by(InterviewSession.id.desc())
    )


async def ensure_bot_user(db: AsyncSession, user_id: int, username: str | None,
                          first_name: str | None, lang: str) -> BotUser:
    user = await db.get(BotUser, user_id)
    if user is None:
        user = BotUser(user_id=user_id, username=username, first_name=first_name, lang=lang)
        db.add(user)
        await db.flush()
    return user


async def start_interview(db: AsyncSession, user: BotUser) -> InterviewSession:
    """Возобновляет незаконченное интервью или создаёт новое."""
    existing = await get_active(db, user.user_id)
    if existing:
        return existing
    session = InterviewSession(user_id=user.user_id, qa_log=[], q_count=0, status=STATUS_ACTIVE)
    db.add(session)
    await db.flush()
    return session


async def is_user_blocked(db: AsyncSession, user_id: int) -> bool:
    return is_blocked(await db.get(BlacklistEntry, user_id))
