from fastapi import APIRouter, Depends

from backend.app.api.deps import require
from backend.app.core.permissions import Perm
from backend.app.services.errors import ServiceError

router = APIRouter(prefix="/employees", tags=["employees"])


@router.get("", dependencies=[Depends(require(Perm.READ))])
async def list_employees() -> None:
    raise ServiceError(501, "Карточки сотрудников будут добавлены после MVP")
