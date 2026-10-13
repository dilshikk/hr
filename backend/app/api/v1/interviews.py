from fastapi import APIRouter, Depends

from backend.app.api.deps import require
from backend.app.core.permissions import Perm
from backend.app.services.errors import ServiceError

router = APIRouter(prefix="/interviews", tags=["interviews"])


@router.get("", dependencies=[Depends(require(Perm.READ))])
async def list_interviews() -> None:
    raise ServiceError(501, "Интервью будут добавлены после MVP")
