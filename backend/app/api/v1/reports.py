from fastapi import APIRouter, Depends

from backend.app.api.deps import require
from backend.app.core.permissions import Perm
from backend.app.services.errors import ServiceError

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("", dependencies=[Depends(require(Perm.READ))])
async def reports() -> None:
    raise ServiceError(501, "Отчёты будут добавлены после MVP")
