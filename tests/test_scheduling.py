from datetime import datetime, timedelta, timezone

import pytest

from app.services.scheduling import (
    InvalidSchedule,
    check_can_cancel,
    check_can_score,
    check_score,
    check_start,
    find_conflict,
    overlaps,
)

T0 = datetime(2026, 10, 20, 10, 0, tzinfo=timezone.utc)


def test_overlapping_intervals_conflict():
    assert overlaps(T0, 60, T0 + timedelta(minutes=30), 60)


def test_back_to_back_is_not_a_conflict():
    assert not overlaps(T0, 30, T0 + timedelta(minutes=30), 30)


def test_inner_interval_conflicts():
    assert overlaps(T0, 120, T0 + timedelta(minutes=30), 15)


def test_find_conflict_returns_first_clashing_id():
    existing = [(1, T0 - timedelta(hours=3), 30), (2, T0 + timedelta(minutes=15), 30)]
    assert find_conflict(T0, 30, existing) == 2
    assert find_conflict(T0, 30, existing[:1]) is None


def test_past_start_is_rejected_but_small_slack_is_allowed():
    check_start(T0 - timedelta(minutes=2), T0)
    with pytest.raises(InvalidSchedule):
        check_start(T0 - timedelta(minutes=30), T0)


def test_only_scheduled_can_be_cancelled():
    check_can_cancel("scheduled")
    for status in ("done", "cancelled"):
        with pytest.raises(InvalidSchedule):
            check_can_cancel(status)


def test_only_scheduled_can_be_scored():
    check_can_score("scheduled")
    for status in ("done", "cancelled"):
        with pytest.raises(InvalidSchedule):
            check_can_score(status)


@pytest.mark.parametrize("score", [0, 6, -1])
def test_score_out_of_range_is_rejected(score):
    with pytest.raises(InvalidSchedule):
        check_score(score)


@pytest.mark.parametrize("score", [1, 3, 5])
def test_score_in_range_is_accepted(score):
    check_score(score)
