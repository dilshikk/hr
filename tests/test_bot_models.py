from app.models import (
    BlacklistEntry,
    BotUser,
    InterviewSession,
    MetroStation,
    Position,
)


def test_bot_tables_do_not_clash_with_hr_tables():
    # Старые users/vacancies переименованы, чтобы не пересекаться с таблицами HR-платформы.
    assert BotUser.__tablename__ == "bot_users"
    assert Position.__tablename__ == "positions"


def test_bot_tables_keep_legacy_columns():
    assert {"user_id", "username", "first_name", "lang"} <= set(BotUser.__table__.columns.keys())
    assert {"user_id", "blocked_at", "unblock_at"} <= set(BlacklistEntry.__table__.columns.keys())
    assert {"name_ru", "name_uz", "name_en", "line", "sort_order", "active"} <= set(
        MetroStation.__table__.columns.keys()
    )
    assert {"name_ru", "name_uz", "emoji", "is_active", "sort_order"} <= set(
        Position.__table__.columns.keys()
    )
    assert {
        "user_id", "qa_log", "q_count", "status",
        "report_resume", "report_skills", "report_personality",
    } <= set(InterviewSession.__table__.columns.keys())


def test_blacklist_unblock_is_optional():
    # Пустой unblock_at означает бессрочную блокировку.
    assert BlacklistEntry.__table__.columns["unblock_at"].nullable is True
