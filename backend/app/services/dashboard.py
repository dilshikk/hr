"""Показатели главной страницы. Чистая логика без БД - легко тестировать."""
from app.services.pipeline import Stage

# Кандидаты, с которыми HR работает прямо сейчас (не новые и не завершённые/отложенные).
IN_PROGRESS = (Stage.REVIEW, Stage.CONTACT, Stage.INTERVIEW, Stage.TRIAL, Stage.OFFER)


def build_summary(stage_counts: dict[str, int], new_last_week: int, open_vacancies: int) -> dict:
    """Собирает показатели из числа кандидатов по этапам.

    Этапы без кандидатов остаются с нулём, чтобы воронка на экране не «прыгала».
    Записи с неизвестным этапом (например, из старых данных) в показатели не входят.
    """
    by_stage = {s.value: stage_counts.get(s.value, 0) for s in Stage}
    return {
        "total": sum(by_stage.values()),
        "new_last_week": new_last_week,
        "in_progress": sum(by_stage[s.value] for s in IN_PROGRESS),
        "hired": by_stage[Stage.HIRED.value],
        "open_vacancies": open_vacancies,
        "by_stage": by_stage,
    }
