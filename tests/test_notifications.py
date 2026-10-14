from app.models import User
from app.services.notifications import (
    new_candidate_text,
    select_recipients,
    stage_changed_text,
)


def make_user(user_id: int, role: str, branch_id: int | None, active: bool = True) -> User:
    return User(id=user_id, telegram_id=1000 + user_id, role=role, branch_id=branch_id, is_active=active)


USERS = [
    make_user(1, "owner", None),
    make_user(2, "hr_admin", None),
    make_user(3, "recruiter", 1),
    make_user(4, "branch_manager", 1),
    make_user(5, "recruiter", 2),
    make_user(6, "viewer", 1),
    make_user(7, "recruiter", 1, active=False),
    make_user(8, "hacker", 1),
]


def ids(users: list[User]) -> set[int]:
    return {u.id for u in users}


def test_branch_staff_and_management_are_notified():
    assert ids(select_recipients(USERS, branch_id=1, exclude_user_id=None)) == {1, 2, 3, 4}


def test_other_branch_staff_is_not_notified():
    # Сотрудник филиала 2 не должен узнавать о кандидатах филиала 1.
    assert 5 not in ids(select_recipients(USERS, branch_id=1, exclude_user_id=None))
    assert 3 not in ids(select_recipients(USERS, branch_id=2, exclude_user_id=None))


def test_author_does_not_get_own_notification():
    assert 3 not in ids(select_recipients(USERS, branch_id=1, exclude_user_id=3))


def test_viewer_inactive_and_unknown_role_are_skipped():
    result = ids(select_recipients(USERS, branch_id=1, exclude_user_id=None))
    assert not ({6, 7, 8} & result)


def test_staff_without_branch_gets_nothing_from_branch_events():
    users = [make_user(9, "recruiter", None)]
    assert select_recipients(users, branch_id=1, exclude_user_id=None) == []


def test_new_candidate_text():
    assert new_candidate_text("Лола Мурадова") == "Новый кандидат: Лола Мурадова"


def test_stage_text_uses_russian_labels():
    assert stage_changed_text("Лола", "new", "review") == "Лола: Новый -> Рассмотрение"


def test_rejection_text_includes_reason():
    text = stage_changed_text("Лола", "interview", "rejected", "не подошёл график")
    assert text.endswith("Причина: не подошёл график")


def test_unknown_stage_is_shown_as_is():
    assert stage_changed_text("Лола", "new", "mystery") == "Лола: Новый -> mystery"
