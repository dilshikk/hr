import pytest

from backend.app.services.pipeline import InvalidTransition, Stage, check_transition


def test_valid_transition():
    assert check_transition("new", "review") is Stage.REVIEW


def test_skip_stage_rejected():
    with pytest.raises(InvalidTransition):
        check_transition("new", "offer")


def test_rejection_requires_reason():
    with pytest.raises(InvalidTransition):
        check_transition("interview", "rejected", "  ")
    assert check_transition("interview", "rejected", "не подошёл график") is Stage.REJECTED


def test_terminal_stage_has_no_exit():
    with pytest.raises(InvalidTransition):
        check_transition("hired", "review")
