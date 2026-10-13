from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import ALL_BRANCHES, Perm, Role, can_access_branch
from app.models import AuditLog, Candidate, PipelineEvent, User
from app.schemas.candidate import CandidateIn, CandidateOut, StageIn
from app.services.pipeline import InvalidTransition, check_transition

router = APIRouter(prefix="/api/v1/candidates", tags=["candidates"])


async def _get_allowed(db: AsyncSession, user: User, candidate_id: int) -> Candidate:
    cand = await db.get(Candidate, candidate_id)
    # 404 вместо 403, чтобы не раскрывать существование чужих записей (защита от IDOR).
    if not cand or not can_access_branch(user.role, user.branch_id, cand.branch_id):
        raise HTTPException(404, "Кандидат не найден")
    return cand


@router.get("", response_model=list[CandidateOut])
async def list_candidates(
    stage: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[Candidate]:
    q = select(Candidate).order_by(Candidate.id.desc()).limit(limit).offset(offset)
    if Role(user.role) not in ALL_BRANCHES:
        if user.branch_id is None:
            return []
        q = q.where(Candidate.branch_id == user.branch_id)
    if stage:
        q = q.where(Candidate.stage == stage)
    return list((await db.scalars(q)).all())


@router.post("", response_model=CandidateOut, status_code=201)
async def create_candidate(
    body: CandidateIn,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    if not can_access_branch(user.role, user.branch_id, body.branch_id):
        raise HTTPException(403, "Нет доступа к филиалу")
    cand = Candidate(**body.model_dump())
    db.add(cand)
    await db.flush()
    db.add(AuditLog(actor_id=user.id, action="candidate.create", target=str(cand.id)))
    await db.commit()
    return cand


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: int,
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    return await _get_allowed(db, user, candidate_id)


@router.post("/{candidate_id}/stage", response_model=CandidateOut)
async def move_stage(
    candidate_id: int,
    body: StageIn,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    cand = await _get_allowed(db, user, candidate_id)
    try:
        new_stage = check_transition(cand.stage, body.stage, body.reason)
    except InvalidTransition as exc:
        raise HTTPException(400, str(exc))
    db.add(PipelineEvent(
        candidate_id=cand.id, actor_id=user.id,
        from_stage=cand.stage, to_stage=new_stage.value, reason=body.reason,
    ))
    cand.stage = new_stage.value
    db.add(AuditLog(actor_id=user.id, action="candidate.stage", target=str(cand.id)))
    await db.commit()
    return cand
