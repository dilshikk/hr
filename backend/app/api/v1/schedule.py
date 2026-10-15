"""Календарь интервью: назначение, отмена, оценка. Изоляция филиалов как у кандидатов."""
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import AwareDatetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import ALL_BRANCHES, Perm, Role, can_access_branch, has_perm
from app.models import AuditLog, Candidate, ScheduledInterview, User, utcnow
from app.schemas.schedule import ScheduleIn, ScheduleOut, ScoreIn
from app.services import scheduling as sch
from app.services.scheduling import InterviewStatus, InvalidSchedule

router = APIRouter(prefix="/api/v1/schedule", tags=["schedule"])
Interviewer = aliased(User)


def _select():
    return (
        select(ScheduledInterview, Candidate.full_name, Interviewer.full_name)
        .join(Candidate, Candidate.id == ScheduledInterview.candidate_id)
        .join(Interviewer, Interviewer.id == ScheduledInterview.interviewer_id)
    )


def _out(row) -> ScheduleOut:
    item, candidate_name, interviewer_name = row
    return ScheduleOut(
        id=item.id, candidate_id=item.candidate_id, candidate_name=candidate_name,
        interviewer_id=item.interviewer_id, interviewer_name=interviewer_name,
        starts_at=item.starts_at, duration_min=item.duration_min, format=item.format,
        status=item.status, score=item.score, comment=item.comment,
    )


async def _load(db: AsyncSession, interview_id: int) -> ScheduleOut:
    row = (await db.execute(_select().where(ScheduledInterview.id == interview_id))).one()
    return _out(row)


async def _get_allowed(db: AsyncSession, user: User, interview_id: int) -> ScheduledInterview:
    item = await db.get(ScheduledInterview, interview_id)
    # 404 вместо 403: не раскрываем существование чужих записей (защита от IDOR).
    if not item or not can_access_branch(user.role, user.branch_id, item.branch_id):
        raise HTTPException(404, "Интервью не найдено")
    return item


async def _finish(db: AsyncSession, item: ScheduledInterview, user: User, action: str, values: dict) -> ScheduleOut:
    # Условное обновление: сработает, только если интервью не успели отменить или оценить параллельно.
    result = await db.execute(
        update(ScheduledInterview)
        .where(ScheduledInterview.id == item.id, ScheduledInterview.status == InterviewStatus.SCHEDULED.value)
        .values(**values)
    )
    if result.rowcount != 1:
        await db.rollback()
        raise HTTPException(409, "Интервью уже изменено. Обновите список")
    db.add(AuditLog(actor_id=user.id, action=action, target=str(item.id)))
    await db.commit()
    return await _load(db, item.id)


@router.get("", response_model=list[ScheduleOut])
async def list_schedule(
    status: InterviewStatus | None = None,
    date_from: AwareDatetime | None = None,
    date_to: AwareDatetime | None = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> list[ScheduleOut]:
    q = _select().order_by(ScheduledInterview.starts_at.asc()).limit(limit).offset(offset)
    if Role(user.role) not in ALL_BRANCHES:
        if user.branch_id is None:
            return []
        q = q.where(ScheduledInterview.branch_id == user.branch_id)
    if status:
        q = q.where(ScheduledInterview.status == status.value)
    if date_from:
        q = q.where(ScheduledInterview.starts_at >= date_from)
    if date_to:
        q = q.where(ScheduledInterview.starts_at < date_to)
    return [_out(r) for r in (await db.execute(q)).all()]


@router.post("", response_model=ScheduleOut, status_code=201)
async def create_interview(
    body: ScheduleIn,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> ScheduleOut:
    cand = await db.get(Candidate, body.candidate_id)
    if not cand or not can_access_branch(user.role, user.branch_id, cand.branch_id):
        raise HTTPException(404, "Кандидат не найден")
    interviewer = await db.get(User, body.interviewer_id)
    # Интервьюер должен быть действующим сотрудником с доступом к филиалу кандидата.
    if (
        not interviewer or not interviewer.is_active
        or not has_perm(interviewer.role, Perm.WRITE_CANDIDATES)
        or not can_access_branch(interviewer.role, interviewer.branch_id, cand.branch_id)
    ):
        raise HTTPException(400, "Этот сотрудник не может проводить интервью")
    try:
        sch.check_start(body.starts_at, utcnow())
    except InvalidSchedule as exc:
        raise HTTPException(400, str(exc))

    end = body.starts_at + timedelta(minutes=body.duration_min)
    window_start = body.starts_at - timedelta(minutes=sch.MAX_DURATION_MIN)
    rows = await db.execute(
        select(ScheduledInterview.id, ScheduledInterview.starts_at, ScheduledInterview.duration_min).where(
            ScheduledInterview.interviewer_id == interviewer.id,
            ScheduledInterview.status == InterviewStatus.SCHEDULED.value,
            ScheduledInterview.starts_at >= window_start,
            ScheduledInterview.starts_at < end,
        )
    )
    if sch.find_conflict(body.starts_at, body.duration_min, rows.all()) is not None:
        raise HTTPException(409, "У интервьюера в это время уже есть интервью")

    item = ScheduledInterview(
        candidate_id=cand.id, branch_id=cand.branch_id, interviewer_id=interviewer.id,
        starts_at=body.starts_at, duration_min=body.duration_min, format=body.format,
        status=InterviewStatus.SCHEDULED.value, comment="", created_by=user.id,
    )
    db.add(item)
    await db.flush()
    db.add(AuditLog(actor_id=user.id, action="interview.schedule", target=str(item.id)))
    await db.commit()
    return await _load(db, item.id)


@router.post("/{interview_id}/cancel", response_model=ScheduleOut)
async def cancel_interview(
    interview_id: int,
    user: User = Depends(require(Perm.WRITE_CANDIDATES)),
    db: AsyncSession = Depends(get_session),
) -> ScheduleOut:
    item = await _get_allowed(db, user, interview_id)
    try:
        sch.check_can_cancel(item.status)
    except InvalidSchedule as exc:
        raise HTTPException(400, str(exc))
    return await _finish(db, item, user, "interview.cancel", {"status": InterviewStatus.CANCELLED.value})


@router.post("/{interview_id}/score", response_model=ScheduleOut)
async def score_interview(
    interview_id: int,
    body: ScoreIn,
    user: User = Depends(require(Perm.READ)),
    db: AsyncSession = Depends(get_session),
) -> ScheduleOut:
    item = await _get_allowed(db, user, interview_id)
    # Оценивает назначенный интервьюер или руководство.
    if user.id != item.interviewer_id and Role(user.role) not in ALL_BRANCHES:
        raise HTTPException(403, "Оценить может только назначенный интервьюер")
    try:
        sch.check_can_score(item.status)
        sch.check_score(body.score)
    except InvalidSchedule as exc:
        raise HTTPException(400, str(exc))
    values = {"status": InterviewStatus.DONE.value, "score": body.score, "comment": body.comment}
    return await _finish(db, item, user, "interview.score", values)
