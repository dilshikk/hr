"""Календарь интервью: чистая логика без БД (время, конфликты, оценки)."""
from collections.abc import Iterable
from datetime import datetime, timedelta
from enum import StrEnum

MAX_DURATION_MIN = 240
START_SLACK = timedelta(minutes=5)  # допуск на разницу часов и задержку при отправке формы
MIN_SCORE, MAX_SCORE = 1, 5


class InterviewStatus(StrEnum):
    SCHEDULED = "scheduled"
    DONE = "done"
    CANCELLED = "cancelled"


class InvalidSchedule(ValueError):
    pass


def overlaps(a_start: datetime, a_min: int, b_start: datetime, b_min: int) -> bool:
    """Пересекаются ли два интервала. Встык (конец одного = начало другого) не считается пересечением."""
    return a_start < b_start + timedelta(minutes=b_min) and b_start < a_start + timedelta(minutes=a_min)


def find_conflict(
    starts_at: datetime, duration_min: int, existing: Iterable[tuple[int, datetime, int]]
) -> int | None:
    """Возвращает id первого пересекающегося интервью или None. existing: (id, начало, минуты)."""
    for interview_id, other_start, other_min in existing:
        if overlaps(starts_at, duration_min, other_start, other_min):
            return interview_id
    return None


def check_start(starts_at: datetime, now: datetime) -> None:
    if starts_at < now - START_SLACK:
        raise InvalidSchedule("Нельзя назначить интервью на прошедшее время")


def check_can_cancel(status: str) -> None:
    if status != InterviewStatus.SCHEDULED:
        raise InvalidSchedule("Отменить можно только запланированное интервью")


def check_can_score(status: str) -> None:
    if status == InterviewStatus.DONE:
        raise InvalidSchedule("Интервью уже оценено")
    if status != InterviewStatus.SCHEDULED:
        raise InvalidSchedule("Оценить можно только запланированное интервью")


def check_score(score: int) -> None:
    if not MIN_SCORE <= score <= MAX_SCORE:
        raise InvalidSchedule(f"Оценка должна быть от {MIN_SCORE} до {MAX_SCORE}")
