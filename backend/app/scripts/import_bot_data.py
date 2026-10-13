"""Одноразовый перенос данных из базы старого бота (mado_jbot) в схему HR-платформы.

Запуск (из корня репозитория, после `alembic upgrade head`):

    OLD_DATABASE_URL=postgresql+asyncpg://user:pass@127.0.0.1:5432/mado_jobs \\
    DATABASE_URL=postgresql+asyncpg://user:pass@127.0.0.1:5432/mado_hr \\
    python -m app.scripts.import_bot_data            # с корня: PYTHONPATH=backend
    python -m app.scripts.import_bot_data --dry-run  # только посчитать, ничего не записывать

Скрипт безопасно запускать повторно: записи с тем же первичным ключом обновляются, а не дублируются.
Старая база только читается.
"""
import argparse
import asyncio
import json
import os
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models import BlacklistEntry, BotUser, InterviewSession, MetroStation, Position


def to_utc(value: datetime | None) -> datetime | None:
    """Старая база хранит время без часового пояса; считаем его UTC."""
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_json(value: object) -> object:
    """JSON из старой базы может прийти строкой (колонка text/json) или уже разобранным."""
    if value is None or value == "":
        return None
    if isinstance(value, (bytes, bytearray)):
        value = value.decode("utf-8")
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            # Не теряем данные: сохраняем исходный текст как есть.
            return {"raw": value}
    return value


def to_bool(value: object) -> bool:
    return bool(int(value)) if isinstance(value, (int, str)) and str(value).isdigit() else bool(value)


def map_position(row: dict) -> Position:
    return Position(
        id=row["id"], name_ru=row["name_ru"], name_uz=row["name_uz"],
        emoji=row.get("emoji") or "", is_active=to_bool(row["is_active"]),
        sort_order=row.get("sort_order") or 0, created_at=to_utc(row.get("created_at")),
    )


def map_metro(row: dict) -> MetroStation:
    return MetroStation(
        id=row["id"], name_ru=row["name_ru"], name_uz=row["name_uz"],
        name_en=row.get("name_en"), line=row["line"],
        sort_order=row.get("sort_order") or 0, active=to_bool(row["active"]),
    )


def map_bot_user(row: dict) -> BotUser:
    return BotUser(
        user_id=row["user_id"], username=row.get("username"),
        first_name=row.get("first_name"), lang=row.get("lang") or "ru",
        created_at=to_utc(row.get("created_at")),
    )


def map_blacklist(row: dict) -> BlacklistEntry:
    return BlacklistEntry(
        user_id=row["user_id"], blocked_at=to_utc(row.get("blocked_at")),
        unblock_at=to_utc(row.get("unblock_at")),
    )


def map_interview(row: dict) -> InterviewSession:
    qa_log = parse_json(row.get("qa_log"))
    return InterviewSession(
        id=row["id"], user_id=row["user_id"],
        qa_log=qa_log if isinstance(qa_log, list) else [],
        q_count=row.get("q_count") or 0, status=row.get("status") or "done",
        report_resume=parse_json(row.get("report_resume")),
        report_skills=parse_json(row.get("report_skills")),
        report_personality=parse_json(row.get("report_personality")),
    )


# Порядок важен: сначала справочники и пользователи, потом таблицы, которые на них ссылаются.
STEPS = (
    ("positions", "vacancies", map_position),
    ("metro_stations", "metro_stations", map_metro),
    ("bot_users", "users", map_bot_user),
    ("blacklist", "blacklist", map_blacklist),
    ("interview_sessions", "interview_sessions", map_interview),
)


async def read_rows(old: AsyncSession, table: str) -> Sequence[dict]:
    # Имя таблицы берётся только из константы STEPS, не из пользовательского ввода.
    result = await old.execute(text(f"SELECT * FROM public.{table}"))
    return [dict(r) for r in result.mappings().all()]


async def ensure_bot_users(new: AsyncSession, user_ids: set[int]) -> int:
    """Чёрный список и интервью ссылаются на пользователя; создаём недостающих заглушками."""
    created = 0
    for user_id in user_ids:
        if await new.get(BotUser, user_id) is None:
            new.add(BotUser(user_id=user_id, lang="ru"))
            created += 1
    await new.flush()
    return created


async def reset_sequence(new: AsyncSession, table: str) -> None:
    """После вставки с готовыми id нужно сдвинуть счётчик, иначе новые записи получат занятые id."""
    if new.bind.dialect.name != "postgresql":
        return
    await new.execute(text(
        f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
        f"COALESCE((SELECT MAX(id) FROM {table}), 1), (SELECT MAX(id) FROM {table}) IS NOT NULL)"
    ))


async def run(old_url: str, new_url: str, dry_run: bool) -> dict[str, int]:
    old_engine = create_async_engine(old_url)
    new_engine = create_async_engine(new_url)
    counts: dict[str, int] = {}
    try:
        async with async_sessionmaker(old_engine)() as old, async_sessionmaker(new_engine)() as new:
            for target, source, mapper in STEPS:
                rows = await read_rows(old, source)
                if target in ("blacklist", "interview_sessions"):
                    await ensure_bot_users(new, {r["user_id"] for r in rows})
                for row in rows:
                    await new.merge(mapper(row))
                await new.flush()
                if target in ("positions", "metro_stations", "interview_sessions"):
                    await reset_sequence(new, target)
                counts[target] = len(rows)
            if dry_run:
                await new.rollback()  # ничего не сохраняем
            else:
                await new.commit()
    finally:
        await old_engine.dispose()
        await new_engine.dispose()
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--dry-run", action="store_true", help="прочитать и проверить, но не записывать")
    args = parser.parse_args()
    old_url, new_url = os.environ.get("OLD_DATABASE_URL"), os.environ.get("DATABASE_URL")
    if not old_url or not new_url:
        raise SystemExit("Нужны переменные OLD_DATABASE_URL (старая база) и DATABASE_URL (новая).")
    counts = asyncio.run(run(old_url, new_url, args.dry_run))
    mode = "ПРОВЕРКА (ничего не записано)" if args.dry_run else "ПЕРЕНОС ЗАВЕРШЁН"
    print(mode)
    for table, count in counts.items():
        print(f"  {table}: {count}")


if __name__ == "__main__":
    main()
