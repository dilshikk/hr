from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.permissions import can_access_branch, has_all_branches
from backend.app.models import Candidate, PipelineEvent, User
from backend.app.repositories import audit, candidates
from backend.app.schemas.candidates import CandidateIn, StageIn
from backend.app.services.errors import ServiceError
from backend.app.services.pipeline import InvalidTransition, check_transition


async def list_for_user(db: AsyncSession, user: User, stage: str | None, limit: int, offset: int) -> list[Candidate]:
    if has_all_branches(user.role):
        return await candidates.list_visible(db, None, stage, limit, offset)
    if user.branch_id is None:
        return []
    return await candidates.list_visible(db, user.branch_id, stage, limit, offset)


async def get_allowed(db: AsyncSession, user: User, candidate_id: int) -> Candidate:
    cand = await candidates.get(db, candidate_id)
    # 404 вместо 403, чтобы не раскрывать существование чужих записей (защита от IDOR).
    if not cand or not can_access_branch(user.role, user.branch_id, cand.branch_id):
        raise ServiceError(404, "Кандидат не найден")
    return cand


async def create(db: AsyncSession, user: User, data: CandidateIn) -> Candidate:
    if not can_access_branch(user.role, user.branch_id, data.branch_id):
        raise ServiceError(403, "Нет доступа к филиалу")
    cand = await candidates.add(db, Candidate(**data.model_dump()))
    audit.log(db, user.id, "candidate.create", str(cand.id))
    await db.commit()
    return cand


async def move_stage(db: AsyncSession, user: User, candidate_id: int, data: StageIn) -> Candidate:
    cand = await get_allowed(db, user, candidate_id)
    try:
        new_stage = check_transition(cand.stage, data.stage, data.reason)
    except InvalidTransition as exc:
        raise ServiceError(400, str(exc))
    candidates.add_event(db, PipelineEvent(
        candidate_id=cand.id, actor_id=user.id,
        from_stage=cand.stage, to_stage=new_stage.value, reason=data.reason,
    ))
    cand.stage = new_stage.value
    audit.log(db, user.id, "candidate.stage", str(cand.id))
    await db.commit()
    return cand
