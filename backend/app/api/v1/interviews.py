"""Просмотр интервью, пройденных в боте.

У интервью нет филиала, поэтому доступ только у ролей, которые видят все филиалы
(Owner, HR Admin): иначе данные кандидатов утекли бы между филиалами.
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import require
from app.core.database import get_session
from app.core.permissions import ALL_BRANCHES, Perm, Role
from app.models import BotUser, InterviewSession, User
from app.schemas.interview import InterviewListItem, InterviewOut

router = APIRouter(prefix="/api/v1/interviews", tags=["interviews"])


async def all_branches_user(user: User = Depends(require(Perm.READ))) -> User:
    try:
        allowed = Role(user.role) in ALL_BRANCHES
    except ValueError:
        allowed = False
    if not allowed:
        raise HTTPException(403, "Недостаточно прав")
    return user


def display_name(bot_user: BotUser | None, user_id: int) -> str:
    if bot_user is None:
        return str(user_id)
    return bot_user.first_name or bot_user.username or str(user_id)


@router.get("", response_model=list[InterviewListItem])
async def list_interviews(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    _: User = Depends(all_branches_user),
    db: AsyncSession = Depends(get_session),
) -> list[InterviewListItem]:
    rows = await db.execute(
        select(InterviewSession, BotUser)
        .outerjoin(BotUser, BotUser.user_id == InterviewSession.user_id)
        .order_by(InterviewSession.id.desc())
        .limit(limit)
        .offset(offset)
    )
    return [
        InterviewListItem(
            id=s.id, user_id=s.user_id, name=display_name(u, s.user_id),
            status=s.status, q_count=s.q_count,
        )
        for s, u in rows.all()
    ]


@router.get("/{interview_id}", response_model=InterviewOut)
async def get_interview(
    interview_id: int,
    _: User = Depends(all_branches_user),
    db: AsyncSession = Depends(get_session),
) -> InterviewOut:
    session = await db.get(InterviewSession, interview_id)
    if session is None:
        raise HTTPException(404, "Интервью не найдено")
    bot_user = await db.get(BotUser, session.user_id)
    return InterviewOut(
        id=session.id, user_id=session.user_id, name=display_name(bot_user, session.user_id),
        status=session.status, q_count=session.q_count, qa_log=session.qa_log,
        report_resume=session.report_resume, report_skills=session.report_skills,
        report_personality=session.report_personality,
    )
