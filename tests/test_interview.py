from datetime import datetime, timedelta, timezone

from app.models import BlacklistEntry, InterviewSession
from app.services.interview import (
    QUESTIONS,
    STATUS_ACTIVE,
    STATUS_DONE,
    apply_answer,
    is_blocked,
    next_question,
)

NOW = datetime(2026, 10, 14, 12, 0, tzinfo=timezone.utc)


def new_session() -> InterviewSession:
    return InterviewSession(user_id=1, qa_log=[], q_count=0, status=STATUS_ACTIVE)


def test_both_languages_have_same_number_of_questions():
    assert len(QUESTIONS["ru"]) == len(QUESTIONS["uz"])


def test_unknown_language_falls_back_to_russian():
    assert next_question("en", 0) == QUESTIONS["ru"][0]


def test_answer_is_recorded_with_its_question():
    session = new_session()
    following = apply_answer(session, "ru", "  Лола, 22  ")
    assert session.qa_log == [{"q": QUESTIONS["ru"][0], "a": "Лола, 22"}]
    assert session.q_count == 1
    assert following == QUESTIONS["ru"][1]
    assert session.status == STATUS_ACTIVE


def test_interview_finishes_after_last_answer():
    session = new_session()
    following = "start"
    for _ in QUESTIONS["ru"]:
        following = apply_answer(session, "ru", "ответ")
    assert following is None
    assert session.status == STATUS_DONE
    assert session.q_count == len(QUESTIONS["ru"])


def test_extra_answer_after_finish_is_ignored():
    session = new_session()
    for _ in QUESTIONS["ru"]:
        apply_answer(session, "ru", "ответ")
    assert apply_answer(session, "ru", "лишнее") is None
    assert session.q_count == len(QUESTIONS["ru"])


def test_long_answer_is_truncated():
    session = new_session()
    apply_answer(session, "ru", "я" * 5000)
    assert len(session.qa_log[0]["a"]) == 2000


def test_not_in_blacklist_is_not_blocked():
    assert not is_blocked(None, NOW)


def test_blacklist_without_end_date_is_permanent():
    assert is_blocked(BlacklistEntry(user_id=1, blocked_at=NOW, unblock_at=None), NOW)


def test_blacklist_expires_on_unblock_date():
    future = BlacklistEntry(user_id=1, blocked_at=NOW, unblock_at=NOW + timedelta(days=1))
    past = BlacklistEntry(user_id=1, blocked_at=NOW, unblock_at=NOW - timedelta(days=1))
    assert is_blocked(future, NOW)
    assert not is_blocked(past, NOW)


def test_naive_unblock_date_is_treated_as_utc():
    naive_past = BlacklistEntry(user_id=1, blocked_at=NOW, unblock_at=datetime(2026, 1, 1))
    assert not is_blocked(naive_past, NOW)
