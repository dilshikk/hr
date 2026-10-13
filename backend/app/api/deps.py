from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_session
from backend.app.core.permissions import Perm, has_perm
from backend.app.models import User
from backend.app.services import auth
from backend.app.services.errors import ServiceError


def bearer(authorization: str = Header(default="")) -> str:
    return authorization.removeprefix("Bearer ").strip()


async def current_user(token: str = Depends(bearer), db: AsyncSession = Depends(get_session)) -> User:
    return await auth.authenticate(db, token)


def require(perm: Perm):
    async def checker(user: User = Depends(current_user)) -> User:
        if not has_perm(user.role, perm):
            raise ServiceError(403, "Недостаточно прав")
        return user

    return checker
