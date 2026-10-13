from app.core.permissions import Perm, can_access_branch, can_manage_user, has_perm


def test_viewer_cannot_write():
    assert has_perm("viewer", Perm.READ)
    assert not has_perm("viewer", Perm.WRITE_CANDIDATES)


def test_unknown_role_has_no_rights():
    assert not has_perm("hacker", Perm.READ)


def test_branch_isolation():
    assert can_access_branch("recruiter", 1, 1)
    assert not can_access_branch("recruiter", 1, 2)
    assert not can_access_branch("recruiter", None, 1)
    assert can_access_branch("hr_admin", None, 2)


def test_only_owner_manages_branches():
    assert has_perm("owner", Perm.MANAGE_BRANCHES)
    assert not has_perm("hr_admin", Perm.MANAGE_BRANCHES)
    assert has_perm("hr_admin", Perm.MANAGE_USERS)
    assert not has_perm("recruiter", Perm.MANAGE_USERS)


def test_cannot_change_self():
    assert not can_manage_user("owner", 1, 1, "owner", "viewer")


def test_owner_can_manage_anyone():
    assert can_manage_user("owner", 1, 2, "hr_admin", "owner")


def test_hr_admin_limits():
    assert can_manage_user("hr_admin", 1, 2, "viewer", "recruiter")
    assert can_manage_user("hr_admin", 1, 2, "recruiter", None)
    assert not can_manage_user("hr_admin", 1, 2, "viewer", "hr_admin")
    assert not can_manage_user("hr_admin", 1, 2, "viewer", "owner")
    assert not can_manage_user("hr_admin", 1, 2, "owner", "viewer")
    assert not can_manage_user("hr_admin", 1, 2, "hr_admin", None)


def test_others_cannot_manage():
    assert not can_manage_user("recruiter", 1, 2, "viewer", "recruiter")
    assert not can_manage_user("bogus", 1, 2, "viewer", None)
