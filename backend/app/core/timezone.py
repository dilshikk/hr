"""Часовой пояс Ташкента. В базе время хранится в UTC, в сообщениях и выгрузках показываем местное."""
from datetime import datetime, timedelta, timezone

TASHKENT = timezone(timedelta(hours=5))  # UTC+5, без перехода на летнее время


def as_utc(value: datetime) -> datetime:
    """Время без часового пояса (например, из SQLite) считаем UTC."""
    return value if value.tzinfo else value.replace(tzinfo=timezone.utc)


def to_tashkent(value: datetime) -> datetime:
    return as_utc(value).astimezone(TASHKENT)
