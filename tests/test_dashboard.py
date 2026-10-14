from app.services.dashboard import build_summary
from app.services.pipeline import Stage


def test_empty_data_gives_zeros_for_every_stage():
    result = build_summary({}, 0, 0)
    assert result["total"] == 0
    assert set(result["by_stage"]) == {s.value for s in Stage}
    assert not any(result["by_stage"].values())


def test_in_progress_counts_only_active_stages():
    counts = {"new": 5, "review": 2, "contact": 1, "interview": 3, "trial": 1, "offer": 1,
              "hired": 4, "rejected": 7, "reserve": 2}
    result = build_summary(counts, 6, 3)
    assert result["in_progress"] == 8  # review + contact + interview + trial + offer
    assert result["hired"] == 4
    assert result["total"] == 26
    assert result["new_last_week"] == 6
    assert result["open_vacancies"] == 3


def test_unknown_stage_from_old_data_is_ignored():
    result = build_summary({"new": 2, "mystery": 9}, 0, 0)
    assert result["total"] == 2
    assert "mystery" not in result["by_stage"]
