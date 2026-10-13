import pytest

from app.services.vacancy import InvalidVacancyStatus, VacancyStatus, check_vacancy_status


def test_draft_can_open_or_close():
    assert check_vacancy_status("draft", "open") is VacancyStatus.OPEN
    assert check_vacancy_status("draft", "closed") is VacancyStatus.CLOSED


def test_reopen_closed():
    assert check_vacancy_status("closed", "open") is VacancyStatus.OPEN


def test_cannot_return_to_draft():
    with pytest.raises(InvalidVacancyStatus):
        check_vacancy_status("open", "draft")


def test_unknown_status():
    with pytest.raises(InvalidVacancyStatus):
        check_vacancy_status("open", "archived")
