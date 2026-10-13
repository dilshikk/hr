from datetime import datetime, timezone

from fastapi import Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.core.permissions import Perm, has_perm
from app.core.security import hash_token
from app.models import AuthSession, User


async def current_user(
    authorization: str = Header(default=""),
    db: AsyncSession = Depends(get_session),
) -> User:
    """Пользователь берётся только из серверной сессии, не из параметров запроса."""
    token = authorization.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(401, "Требуется вход")
    row = await db.scalar(select(AuthSession).where(AuthSession.token_hash == hash_token(token)))
    now = datetime.now(timezone.utc)
    if not row or row.revoked or row.expires_at.replace(tzinfo=timezone.utc) < now:
        raise HTTPException(401, "Сессия недействительна")
    user = await db.get(User, row.user_id)
    if not user or not user.is_active:
        raise HTTPException(403, "Доступ закрыт")
    return user


def require(perm: Perm):
    async def checker(user: User = Depends(current_user)) -> User:
        if not has_perm(user.role, perm):
            raise HTTPException(403, "Недостаточно прав")
        return user

    return checker
