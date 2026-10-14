from typing import Literal

from pydantic import BaseModel, Field


class TelegramAuthIn(BaseModel):
    init_data: str = Field(min_length=1, max_length=4096)


class SessionOut(BaseModel):
    """Для Owner и HR Admin вместо token приходит twofa + challenge: нужен второй шаг входа."""
    token: str | None = None
    role: str
    twofa: Literal["setup", "verify"] | None = None
    challenge: str | None = None
    recovery_codes: list[str] | None = None  # показываются один раз, при включении 2FA


class TwoFactorStartIn(BaseModel):
    challenge: str = Field(min_length=1, max_length=256)


class TwoFactorCodeIn(BaseModel):
    challenge: str = Field(min_length=1, max_length=256)
    code: str = Field(min_length=6, max_length=32)  # 6 цифр или код восстановления


class TwoFactorSetupOut(BaseModel):
    secret: str
    uri: str
