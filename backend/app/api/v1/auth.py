from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.api.deps import bearer, current_user
from backend.app.core.database import get_session
from backend.app.models import User
from backend.app.schemas.auth import MeOut, SessionOut, TelegramAuthIn
from backend.app.services import auth

router = APIRouter(tags=["auth"])


@router.post("/auth/telegram", response_model=SessionOut)
async def auth_telegram(body: TelegramAuthIn, db: AsyncSession = Depends(get_session)) -> SessionOut:
    token, role = await auth.login(db, body.init_data)
    return SessionOut(token=token, role=role)


@router.post("/auth/logout")
async def logout(
    token: str = Depends(bearer),
    user: User = Depends(current_user),
    db: AsyncSession = Depends(get_session),
) -> dict:
    await auth.logout(db, user, token)
    return {"ok": True}


@router.get("/me", response_model=MeOut)
async def me(user: User = Depends(current_user)) -> MeOut:
    return MeOut(id=user.id, name=user.full_name, role=user.role, branch_id=user.branch_id)
