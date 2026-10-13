"""Проверка Telegram initData, токены сессий. Без доступа к БД."""
import hashlib
import hmac
import json
import secrets
import time
from urllib.parse import parse_qsl


class InitDataError(ValueError):
    pass


def validate_init_data(init_data: str, bot_token: str, max_age_seconds: int, now: float | None = None) -> dict:
    """Возвращает данные пользователя Telegram или выбрасывает InitDataError."""
    if not bot_token:
        raise InitDataError("BOT_TOKEN не настроен")
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received_hash = pairs.pop("hash", None)
    if not received_hash:
        raise InitDataError("Нет подписи")

    check_string = "\n".join(f"{k}={v}" for k, v in sorted(pairs.items()))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received_hash):
        raise InitDataError("Неверная подпись")

    try:
        auth_date = int(pairs.get("auth_date", "0"))
    except ValueError as exc:
        raise InitDataError("Неверная дата") from exc
    if (now or time.time()) - auth_date > max_age_seconds:
        raise InitDataError("Данные устарели")

    try:
        user = json.loads(pairs.get("user", ""))
    except json.JSONDecodeError as exc:
        raise InitDataError("Нет данных пользователя") from exc
    if not isinstance(user.get("id"), int):
        raise InitDataError("Нет Telegram ID")
    return user


def new_token() -> str:
    return secrets.token_urlsafe(32)


def hash_token(token: str) -> str:
    # В БД хранится только хеш: утечка базы не раскрывает рабочие токены.
    return hashlib.sha256(token.encode()).hexdigest()
