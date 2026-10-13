import logging

from app.core.config import get_settings


def setup_logging() -> None:
    s = get_settings()
    handlers: list[logging.Handler] = [logging.StreamHandler()]
    if s.log_path:
        handlers.append(logging.FileHandler(s.log_path, encoding="utf-8"))
    logging.basicConfig(
        level=s.log_level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )
