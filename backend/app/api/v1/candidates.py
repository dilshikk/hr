from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import require
from backend.app.core.database import get_session
from backend.app.core.permissions import Perm
from backend.app.models import Candidate, User
from backend.app.schemas.candidates import CandidateIn, CandidateOut, StageIn
from backend.app.services import candidates

router = APIRouter(prefix="/candidates", tags=["candidates"])


@router.get("", response_model=list[CandidateOut])
async def list_candidates(
    stage: str | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[Candidate]:
    return await candidates.list_for_user(db, user, stage, limit, offset)


@router.post("", response_model=CandidateOut, status_code=201)
async def create_candidate(
    body: CandidateIn,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    return await candidates.create(db, user, body)


@router.get("/{candidate_id}", response_model=CandidateOut)
async def get_candidate(
    candidate_id: int,
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    return await candidates.get_allowed(db, user, candidate_id)


@router.post("/{candidate_id}/stage", response_model=CandidateOut)
async def move_stage(
    candidate_id: int,
    body: StageIn,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> Candidate:
    return await candidates.move_stage(db, user, candidate_id, body)
