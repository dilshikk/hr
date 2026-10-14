import secrets
from datetime import timedelta

from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import current_user
from app.core.config import Settings, get_settings
from app.core.database import get_session
from app.core.permissions import Role
from app.core.rate_limit import RateLimiter, login_limiter
from app.core.security import InitDataError, hash_token, validate_init_data
from app.core.totp import (
    TotpError,
    decrypt_secret,
    encrypt_secret,
    generate_recovery_codes,
    hash_recovery_code,
    is_totp_format,
    make_challenge,
    new_secret,
    provisioning_uri,
    read_challenge,
    requires_2fa,
    verify_code,
)
from app.models import AuditLog, AuthSession, RecoveryCode, User, UserTotp, utcnow
from app.schemas.auth import (
    SessionOut,
    TelegramAuthIn,
    TwoFactorCodeIn,
    TwoFactorSetupOut,
    TwoFactorStartIn,
)

router = APIRouter(prefix="/api/v1", tags=["auth"])

# 5 попыток ввода кода за 5 минут на одного сотрудника: код из 6 цифр иначе можно подобрать.
twofa_limiter = RateLimiter(max_hits=5, window_seconds=300)


def _client_ip(request: Request) -> str:
    # IP берётся от uvicorn; за nginx он корректен благодаря --proxy-headers (доверие только 127.0.0.1).
    return request.client.host if request.client else "unknown"


def _check_login_rate(ip: str) -> None:
    if not login_limiter.allow(ip):
        raise HTTPException(429, "Слишком много попыток входа. Попробуйте через минуту")


def _require_2fa_keys(s: Settings) -> None:
    # Если ключи не заданы, лучше не пускать Owner/HR Admin, чем пустить без второго шага.
    if not s.session_secret or not s.totp_encryption_key:
        raise HTTPException(503, "2FA не настроена на сервере")


def _add_session(db: AsyncSession, user: User, ip: str, s: Settings) -> str:
    token = secrets.token_urlsafe(32)
    db.add(AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        expires_at=utcnow() + timedelta(minutes=s.session_ttl_minutes),
    ))
    db.add(AuditLog(actor_id=user.id, action="login", target=ip[:64]))
    return token


async def _user_from_challenge(db: AsyncSession, challenge: str, s: Settings) -> User:
    _require_2fa_keys(s)
    try:
        user_id = read_challenge(challenge, s.session_secret)
    except TotpError:
        raise HTTPException(401, "Время подтверждения истекло. Войдите заново")
    user = await db.get(User, user_id)
    # Роль могли изменить после первого шага - проверяем заново.
    if not user or not user.is_active or not requires_2fa(user.role):
        raise HTTPException(403, "Доступ закрыт")
    return user


async def _get_totp(db: AsyncSession, user_id: int) -> UserTotp | None:
    return await db.scalar(select(UserTotp).where(UserTotp.user_id == user_id))


async def _fail(db: AsyncSession, user: User, action: str, ip: str) -> None:
    db.add(AuditLog(actor_id=user.id, action=action, target=ip[:64]))
    await db.commit()
    raise HTTPException(401, "Неверный код")


async def _use_recovery_code(db: AsyncSession, user_id: int, code: str) -> bool:
    row = await db.scalar(select(RecoveryCode).where(
        RecoveryCode.user_id == user_id,
        RecoveryCode.code_hash == hash_recovery_code(code),
        RecoveryCode.used.is_(False),
    ))
    if row is None:
        return False
    row.used = True
    return True


@router.post("/auth/telegram", response_model=SessionOut)
async def auth_telegram(
    body: TelegramAuthIn,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> SessionOut:
    ip = _client_ip(request)
    _check_login_rate(ip)

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

    if requires_2fa(user.role):
        _require_2fa_keys(s)
        totp = await _get_totp(db, user.id)
        db.add(AuditLog(actor_id=user.id, action="login.2fa_required", target=ip[:64]))
        await db.commit()
        return SessionOut(
            role=user.role,
            twofa="verify" if totp and totp.confirmed else "setup",
            challenge=make_challenge(user.id, s.session_secret, s.twofa_challenge_ttl_seconds),
        )

    token = _add_session(db, user, ip, s)
    await db.commit()
    return SessionOut(token=token, role=user.role)


@router.post("/auth/2fa/setup", response_model=TwoFactorSetupOut)
async def twofa_setup(
    body: TwoFactorStartIn,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> TwoFactorSetupOut:
    """Выдаёт новый секрет для приложения-аутентификатора. Пока код не подтверждён, 2FA не включена."""
    ip = _client_ip(request)
    _check_login_rate(ip)
    s = get_settings()
    user = await _user_from_challenge(db, body.challenge, s)
    totp = await _get_totp(db, user.id)
    if totp and totp.confirmed:
        raise HTTPException(400, "2FA уже настроена")

    secret = new_secret()
    encrypted = encrypt_secret(secret, s.totp_encryption_key)
    if totp:
        totp.secret_enc = encrypted
    else:
        db.add(UserTotp(user_id=user.id, secret_enc=encrypted))
    db.add(AuditLog(actor_id=user.id, action="2fa.setup", target=ip[:64]))
    await db.commit()
    return TwoFactorSetupOut(secret=secret, uri=provisioning_uri(secret, user.full_name or f"user{user.id}"))


@router.post("/auth/2fa/confirm", response_model=SessionOut)
async def twofa_confirm(
    body: TwoFactorCodeIn,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> SessionOut:
    """Подтверждает первый код: включает 2FA, выдаёт коды восстановления и сессию."""
    ip = _client_ip(request)
    _check_login_rate(ip)
    s = get_settings()
    user = await _user_from_challenge(db, body.challenge, s)
    if not twofa_limiter.allow(str(user.id)):
        raise HTTPException(429, "Слишком много попыток. Подождите несколько минут")
    totp = await _get_totp(db, user.id)
    if not totp or totp.confirmed:
        raise HTTPException(400, "Сначала запросите настройку 2FA")

    step = verify_code(decrypt_secret(totp.secret_enc, s.totp_encryption_key), body.code)
    if step is None:
        await _fail(db, user, "2fa.confirm_failed", ip)
    totp.confirmed = True
    totp.last_step = step
    codes = generate_recovery_codes()
    db.add_all(RecoveryCode(user_id=user.id, code_hash=hash_recovery_code(c)) for c in codes)
    db.add(AuditLog(actor_id=user.id, action="2fa.enabled", target=ip[:64]))
    token = _add_session(db, user, ip, s)
    await db.commit()
    return SessionOut(token=token, role=user.role, recovery_codes=codes)


@router.post("/auth/2fa/verify", response_model=SessionOut)
async def twofa_verify(
    body: TwoFactorCodeIn,
    request: Request,
    db: AsyncSession = Depends(get_session),
) -> SessionOut:
    """Второй шаг входа: код из приложения или одноразовый код восстановления."""
    ip = _client_ip(request)
    _check_login_rate(ip)
    s = get_settings()
    user = await _user_from_challenge(db, body.challenge, s)
    if not twofa_limiter.allow(str(user.id)):
        raise HTTPException(429, "Слишком много попыток. Подождите несколько минут")
    totp = await _get_totp(db, user.id)
    if not totp or not totp.confirmed:
        raise HTTPException(400, "2FA не настроена")

    if is_totp_format(body.code):
        step = verify_code(decrypt_secret(totp.secret_enc, s.totp_encryption_key), body.code)
        # step должен быть новее последнего принятого: перехваченный код повторно не сработает.
        accepted = step is not None and step > totp.last_step
        if accepted:
            totp.last_step = step
    else:
        accepted = await _use_recovery_code(db, user.id, body.code)
    if not accepted:
        await _fail(db, user, "login.2fa_failed", ip)

    token = _add_session(db, user, ip, s)
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
