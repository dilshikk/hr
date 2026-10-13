from fastapi import APIRouter, Depends

from backend.app.api.deps import require
from backend.app.core.permissions import Perm
from backend.app.services.errors import ServiceError

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/audit", dependencies=[Depends(require(Perm.READ_AUDIT))])
async def audit_log() -> None:
    raise ServiceError(501, "Просмотр журнала будет добавлен после MVP")
