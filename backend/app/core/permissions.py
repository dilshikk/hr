"""Роли и права. Проверяются на сервере при каждом запросе."""
from enum import StrEnum


class Role(StrEnum):
    OWNER = "owner"
    HR_ADMIN = "hr_admin"
    RECRUITER = "recruiter"
    BRANCH_MANAGER = "branch_manager"
    VIEWER = "viewer"


class Perm(StrEnum):
    READ = "read"
    WRITE_CANDIDATES = "write_candidates"
    WRITE_VACANCIES = "write_vacancies"
    READ_AUDIT = "read_audit"
    MANAGE_USERS = "manage_users"
    MANAGE_BRANCHES = "manage_branches"


ALL_BRANCHES = {Role.OWNER, Role.HR_ADMIN}

PERMS: dict[Role, set[Perm]] = {
    Role.OWNER: set(Perm),
    Role.HR_ADMIN: set(Perm) - {Perm.MANAGE_BRANCHES},
    Role.RECRUITER: {Perm.READ, Perm.WRITE_CANDIDATES},
    Role.BRANCH_MANAGER: {Perm.READ, Perm.WRITE_CANDIDATES},
    Role.VIEWER: {Perm.READ},
}


def has_perm(role: str, perm: Perm) -> bool:
    try:
        return perm in PERMS[Role(role)]
    except (ValueError, KeyError):
        return False


def can_access_branch(role: str, user_branch_id: int | None, branch_id: int) -> bool:
    """Изоляция филиалов: Owner/HR Admin видят всё, остальные — только свой филиал."""
    try:
        if Role(role) in ALL_BRANCHES:
            return True
    except ValueError:
        return False
    return user_branch_id is not None and user_branch_id == branch_id


def can_manage_user(actor_role: str, actor_id: int, target_id: int, target_role: str, new_role: str | None) -> bool:
    """Кто кого может менять.
    - себя менять нельзя (защита от случайной потери доступа и самоповышения);
    - Owner может всё;
    - HR Admin не может трогать Owner/HR Admin и не может назначать эти роли.
    """
    if actor_id == target_id:
        return False
    try:
        actor = Role(actor_role)
        target = Role(target_role)
        new = Role(new_role) if new_role is not None else None
    except ValueError:
        return False
    if actor is Role.OWNER:
        return True
    if actor is Role.HR_ADMIN:
        return target not in ALL_BRANCHES and (new is None or new not in ALL_BRANCHES)
    return False
