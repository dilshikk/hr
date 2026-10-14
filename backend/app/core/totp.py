"""2FA (TOTP) для Owner и HR Admin. Чистая логика без БД - легко тестировать.

Вход идёт в два шага: Telegram initData даёт короткий подписанный «челлендж»,
и только вместе с верным кодом из приложения-аутентификатора выдаётся сессия.
"""
import base64
import hashlib
import hmac
import secrets
import time

import pyotp
from cryptography.fernet import Fernet, InvalidToken

from app.core.permissions import Role

TWOFA_ROLES = {Role.OWNER, Role.HR_ADMIN}
STEP_SECONDS = 30
WINDOW_STEPS = 1  # допускаем код предыдущего/следующего шага (расхождение часов)
RECOVERY_CODES_COUNT = 8
ISSUER = "MADO HR"


class TotpError(ValueError):
    pass


def requires_2fa(role: str) -> bool:
    try:
        return Role(role) in TWOFA_ROLES
    except ValueError:
        return False


def _fernet(key: str) -> Fernet:
    if not key:
        raise TotpError("Ключ шифрования 2FA не задан")
    # Ключ из .env может быть любой строкой: приводим его к 32 байтам для Fernet.
    return Fernet(base64.urlsafe_b64encode(hashlib.sha256(key.encode()).digest()))


def encrypt_secret(secret: str, key: str) -> str:
    return _fernet(key).encrypt(secret.encode()).decode()


def decrypt_secret(token: str, key: str) -> str:
    try:
        return _fernet(key).decrypt(token.encode()).decode()
    except InvalidToken as exc:
        raise TotpError("Не удалось расшифровать секрет 2FA") from exc


def new_secret() -> str:
    return pyotp.random_base32()


def provisioning_uri(secret: str, account: str) -> str:
    return pyotp.TOTP(secret, interval=STEP_SECONDS).provisioning_uri(name=account, issuer_name=ISSUER)


def normalize_code(code: str) -> str:
    return "".join(code.split())


def is_totp_format(code: str) -> bool:
    code = normalize_code(code)
    return len(code) == 6 and code.isdigit()


def verify_code(secret: str, code: str, now: float | None = None) -> int | None:
    """Возвращает номер временного шага, к которому подошёл код, или None.

    Номер шага нужен вызывающему коду, чтобы не принять один и тот же код дважды.
    """
    if not is_totp_format(code):
        return None
    code = normalize_code(code)
    current = int((time.time() if now is None else now) // STEP_SECONDS)
    totp = pyotp.TOTP(secret, interval=STEP_SECONDS)
    for step in range(current - WINDOW_STEPS, current + WINDOW_STEPS + 1):
        if hmac.compare_digest(totp.generate_otp(step), code):
            return step
    return None


def generate_recovery_codes(count: int = RECOVERY_CODES_COUNT) -> list[str]:
    return [f"{secrets.token_hex(4)}-{secrets.token_hex(4)}" for _ in range(count)]


def hash_recovery_code(code: str) -> str:
    normalized = "".join(code.lower().replace("-", "").split())
    return hashlib.sha256(normalized.encode()).hexdigest()


def _sign(payload: str, key: str) -> str:
    return hmac.new(key.encode(), payload.encode(), hashlib.sha256).hexdigest()


def make_challenge(user_id: int, key: str, ttl_seconds: int, now: float | None = None) -> str:
    """Подписанная метка «Telegram-вход подтверждён, нужен код». Сама по себе сессию не даёт."""
    if not key:
        raise TotpError("SESSION_SECRET не задан")
    expires = int((time.time() if now is None else now)) + ttl_seconds
    payload = f"{user_id}.{expires}"
    return f"{payload}.{_sign(payload, key)}"


def read_challenge(token: str, key: str, now: float | None = None) -> int:
    """Возвращает ID сотрудника или выбрасывает TotpError (подделка, истёк срок)."""
    if not key:
        raise TotpError("SESSION_SECRET не задан")
    parts = token.split(".")
    if len(parts) != 3 or not parts[0].isdigit() or not parts[1].isdigit():
        raise TotpError("Неверный формат")
    user_id, expires, signature = parts
    if not hmac.compare_digest(signature, _sign(f"{user_id}.{expires}", key)):
        raise TotpError("Неверная подпись")
    if int(expires) < (time.time() if now is None else now):
        raise TotpError("Срок истёк")
    return int(user_id)
