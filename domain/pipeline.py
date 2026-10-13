"""Правила воронки найма. Чистая логика без БД — легко тестировать."""
from enum import StrEnum


class Stage(StrEnum):
    NEW = "new"
    REVIEW = "review"
    CONTACT = "contact"
    INTERVIEW = "interview"
    TRIAL = "trial"
    OFFER = "offer"
    HIRED = "hired"
    REJECTED = "rejected"
    RESERVE = "reserve"


TERMINAL = {Stage.HIRED, Stage.REJECTED}

TRANSITIONS: dict[Stage, set[Stage]] = {
    Stage.NEW: {Stage.REVIEW, Stage.REJECTED, Stage.RESERVE},
    Stage.REVIEW: {Stage.CONTACT, Stage.REJECTED, Stage.RESERVE},
    Stage.CONTACT: {Stage.INTERVIEW, Stage.REJECTED, Stage.RESERVE},
    Stage.INTERVIEW: {Stage.TRIAL, Stage.OFFER, Stage.REJECTED, Stage.RESERVE},
    Stage.TRIAL: {Stage.OFFER, Stage.REJECTED, Stage.RESERVE},
    Stage.OFFER: {Stage.HIRED, Stage.REJECTED, Stage.RESERVE},
    Stage.RESERVE: {Stage.REVIEW, Stage.CONTACT, Stage.REJECTED},
    Stage.HIRED: set(),
    Stage.REJECTED: set(),
}


class InvalidTransition(ValueError):
    pass


def check_transition(current: str, target: str, reason: str = "") -> Stage:
    """Проверяет переход и возвращает целевой этап. Отказ требует причину."""
    try:
        src, dst = Stage(current), Stage(target)
    except ValueError as exc:
        raise InvalidTransition(f"Неизвестный этап: {exc}") from exc
    if dst not in TRANSITIONS[src]:
        raise InvalidTransition(f"Переход {src} -> {dst} недопустим")
    if dst is Stage.REJECTED and not reason.strip():
        raise InvalidTransition("Для отказа нужна причина")
    return dst
