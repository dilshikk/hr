from security.rbac import Perm, can_access_branch, has_perm


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
