from datetime import datetime

from pydantic import BaseModel


class AuditOut(BaseModel):
    id: int
    actor_id: int | None
    actor_name: str | None
    action: str
    target: str
    created_at: datetime
