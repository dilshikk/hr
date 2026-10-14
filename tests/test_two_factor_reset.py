from app.services.two_factor_reset import can_reset_2fa


def test_owner_can_reset_other_privileged_employee():
    assert can_reset_2fa("owner", 1, 2, "hr_admin")
    assert can_reset_2fa("owner", 1, 3, "owner")


def test_owner_cannot_reset_own_2fa():
    # Украденная сессия не должна смочь снять защиту.
    assert not can_reset_2fa("owner", 1, 1, "owner")


def test_hr_admin_cannot_reset_anyone():
    assert not can_reset_2fa("hr_admin", 2, 1, "owner")
    assert not can_reset_2fa("hr_admin", 2, 3, "hr_admin")


def test_other_roles_cannot_reset():
    for role in ("recruiter", "branch_manager", "viewer", "hacker"):
        assert not can_reset_2fa(role, 5, 1, "owner")


def test_reset_makes_no_sense_for_roles_without_2fa():
    assert not can_reset_2fa("owner", 1, 4, "recruiter")
    assert not can_reset_2fa("owner", 1, 4, "viewer")
