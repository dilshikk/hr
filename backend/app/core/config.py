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
    log_path: str = ""  # пусто — логи только в консоль
    webapp_url: str = ""
    session_secret: str = ""
    session_ttl_minutes: int = 480
    init_data_max_age_seconds: int = 3600
    allowed_origins: str = ""  # CORS, через запятую
    totp_encryption_key: str = ""  # ключ шифрования секретов 2FA; без него Owner/HR Admin войти не смогут
    twofa_challenge_ttl_seconds: int = 300  # сколько действует шаг «введите код» после проверки Telegram
    upload_dir: str = "./uploads"  # документы кандидатов; каталог не должен раздаваться через nginx
    openai_api_key: str = ""  # без ключа автоотчёт по интервью недоступен (ответ 503)
    openai_model: str = "gpt-6-luna"
    reminder_interval_seconds: int = 300  # как часто проверять напоминания (не меньше 60)

    @property
    def admin_id_set(self) -> set[int]:
        return {int(x) for x in self.admin_ids.split(",") if x.strip().isdigit()}

    @property
    def origins(self) -> list[str]:
        return [x.strip() for x in self.allowed_origins.split(",") if x.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
