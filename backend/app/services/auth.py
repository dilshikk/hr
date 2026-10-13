from datetime import datetime, timedelta, timezone

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.core.permissions import Role
from backend.app.core.security import InitDataError, hash_token, new_token, validate_init_data
from backend.app.models import AuthSession, User
from backend.app.models.base import utcnow
from backend.app.repositories import audit, users
from backend.app.services.errors import ServiceError


async def login(db: AsyncSession, init_data: str) -> tuple[str, str]:
    s = get_settings()
    try:
        tg = validate_init_data(init_data, s.bot_token, s.init_data_max_age_seconds)
    except InitDataError:
        raise ServiceError(401, "Не удалось подтвердить вход")  # детали не раскрываем

    user = await users.get_by_telegram_id(db, tg["id"])
    if not user:
        # Первый вход: Owner только для ID из ADMIN_IDS, остальные — viewer до назначения роли.
        role = Role.OWNER if tg["id"] in s.admin_id_set else Role.VIEWER
        name = " ".join(filter(None, [tg.get("first_name"), tg.get("last_name")]))
        user = await users.add(db, User(telegram_id=tg["id"], full_name=name, role=role))
    if not user.is_active:
        raise ServiceError(403, "Доступ закрыт")

    token = new_token()
    users.add_session(db, AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=utcnow() + timedelta(minutes=s.session_ttl_minutes),
    ))
    audit.log(db, user.id, "login")
    await db.commit()
    return token, user.role


async def authenticate(db: AsyncSession, token: str) -> User:
    """Пользователь берётся только из серверной сессии."""
    if not token:
        raise ServiceError(401, "Требуется вход")
    row = await users.find_session(db, hash_token(token))
    if not row or row.revoked or row.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise ServiceError(401, "Сессия недействительна")
    user = await users.get(db, row.user_id)
    if not user or not user.is_active:
        raise ServiceError(403, "Доступ закрыт")
    return user


async def logout(db: AsyncSession, user: User, token: str) -> None:
    await users.revoke_session(db, hash_token(token))
    audit.log(db, user.id, "logout")
    await db.commit()
