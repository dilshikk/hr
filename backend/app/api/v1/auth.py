import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.core.config import get_settings
from app.core.database import get_session
from app.core.permissions import Role
from app.core.rate_limit import login_limiter
from app.core.security import InitDataError, hash_token, validate_init_data
from app.models import AuditLog, AuthSession, User, utcnow
from app.schemas.auth import SessionOut, TelegramAuthIn

router = APIRouter(prefix="/api/v1", tags=["auth"])


@router.post("/auth/telegram", response_model=SessionOut)
async def auth_telegram(
    body: TelegramAuthIn,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> SessionOut:
    # IP берётся от uvicorn; за nginx он корректен благодаря --proxy-headers (доверие только 127.0.0.1).
    ip = request.client.host if request.client else "unknown"
    if not login_limiter.allow(ip):
        raise HTTPException(429, "Слишком много попыток входа. Попробуйте через минуту")

    s = get_settings()
    try:
        tg_user = validate_init_data(body.init_data, s.bot_token, s.init_data_max_age_seconds)
    except InitDataError:
        raise HTTPException(401, "Не удалось подтвердить вход")  # детали не раскрываем

    user = await db.scalar(select(User).where(User.telegram_id == tg_user["id"]))
    if not user:
        # Первый вход: Owner только для ID из ADMIN_IDS, остальные — viewer до назначения роли.
        role = Role.OWNER if tg_user["id"] in s.admin_id_set else Role.VIEWER
        name = " ".join(filter(None, [tg_user.get("first_name"), tg_user.get("last_name")]))
        user = User(telegram_id=tg_user["id"], full_name=name, role=role)
        db.add(user)
        await db.flush()
    if not user.is_active:
        raise HTTPException(403, "Доступ закрыт")

    token = secrets.token_urlsafe(32)
    db.add(AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=utcnow() + timedelta(minutes=s.session_ttl_minutes),
    ))
    db.add(AuditLog(actor_id=user.id, action="login", target=ip[:64]))
    await db.commit()
    return SessionOut(token=token, role=user.role)


@router.post("/auth/logout")
async def logout(
    authorization: str = Header(default=""),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    token = authorization.removeprefix("Bearer ").strip()
    await db.execute(update(AuthSession).where(AuthSession.token_hash == hash_token(token)).values(revoked=True))
    db.add(AuditLog(actor_id=user.id, action="logout"))
    await db.commit()
    return {"ok": True}


@router.get("/me")
async def me(user: User = Depends(current_user)) -> dict:
    return {"id": user.id, "name": user.full_name, "role": user.role, "branch_id": user.branch_id}
