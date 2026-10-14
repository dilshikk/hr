from datetime import datetime, timedelta, timezone

from app.scripts.import_bot_data import (
    map_blacklist,
    map_interview,
    map_position,
    parse_json,
    to_bool,
    to_utc,
)


def test_naive_datetime_is_treated_as_utc():
    result = to_utc(datetime(2026, 7, 5, 8, 22, 11))
    assert result == datetime(2026, 7, 5, 8, 22, 11, tzinfo=timezone.utc)


def test_aware_datetime_is_converted_to_utc():
    tashkent = timezone(timedelta(hours=5))
    assert to_utc(datetime(2026, 7, 5, 13, 0, tzinfo=tashkent)).hour == 8


def test_parse_json_handles_string_object_and_empty():
    assert parse_json('{"error": "no_text"}') == {"error": "no_text"}
    assert parse_json([{"q": "a"}]) == [{"q": "a"}]
    assert parse_json("") is None
    assert parse_json(None) is None


def test_parse_json_keeps_broken_text_instead_of_losing_it():
    assert parse_json("не json") == {"raw": "не json"}


def test_to_bool_accepts_legacy_integers():
    assert to_bool(1) is True
    assert to_bool(0) is False
    assert to_bool(True) is True


def test_blacklist_without_unblock_date_stays_permanent():
    entry = map_blacklist({"user_id": 1, "blocked_at": datetime(2026, 7, 5), "unblock_at": None})
    assert entry.unblock_at is None


def test_interview_with_empty_log_is_imported_as_empty_list():
    session = map_interview({
        "id": 24, "user_id": 8865835040, "qa_log": "[]", "q_count": 0,
        "status": "done", "report_resume": '{"error": "no_text"}',
        "report_skills": None, "report_personality": None,
    })
    assert session.qa_log == []
    assert session.report_resume == {"error": "no_text"}
    assert session.report_skills is None


def test_position_keeps_legacy_id_and_activity_flag():
    position = map_position({
        "id": 4, "name_ru": "Бариста", "name_uz": "Barista", "emoji": "",
        "is_active": 1, "sort_order": 3, "created_at": datetime(2026, 8, 5),
    })
    assert position.id == 4 and position.is_active is True
