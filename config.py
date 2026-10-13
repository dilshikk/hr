"""Настройки приложения. Все секреты берутся из окружения (.env), не из кода."""
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    bot_token: str = ""
    admin_ids: str = ""  # Telegram ID через запятую; стартовые Owner
    admin_chat_id: str = ""
    database_url: str = "sqlite+aiosqlite:///./mado_hr.db"
    log_level: str = "INFO"
    webapp_url: str = ""
    session_secret: str = ""
    session_ttl_minutes: int = 480
    init_data_max_age_seconds: int = 3600
    allowed_origins: str = ""  # CORS, через запятую

    @property
    def admin_id_set(self) -> set[int]:
        return {int(x) for x in self.admin_ids.split(",") if x.strip().isdigit()}

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
