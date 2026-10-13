"""Статусы вакансии. Чистая логика без БД."""
from enum import StrEnum


class VacancyStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"


VACANCY_TRANSITIONS: dict[VacancyStatus, set[VacancyStatus]] = {
    VacancyStatus.DRAFT: {VacancyStatus.OPEN, VacancyStatus.CLOSED},
    VacancyStatus.OPEN: {VacancyStatus.CLOSED},
    VacancyStatus.CLOSED: {VacancyStatus.OPEN},
}


class InvalidVacancyStatus(ValueError):
    pass


def check_vacancy_status(current: str, target: str) -> VacancyStatus:
    try:
        src, dst = VacancyStatus(current), VacancyStatus(target)
    except ValueError as exc:
        raise InvalidVacancyStatus("Неизвестный статус вакансии") from exc
    if dst not in VACANCY_TRANSITIONS[src]:
        raise InvalidVacancyStatus("Такая смена статуса недопустима")
    return dst
