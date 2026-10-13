from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models import AuthSession, User


async def get(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    return await db.scalar(select(User).where(User.telegram_id == telegram_id))


async def add(db: AsyncSession, user: User) -> User:
    db.add(user)
    await db.flush()
    return user


def add_session(db: AsyncSession, session: AuthSession) -> None:
    db.add(session)


async def find_session(db: AsyncSession, token_hash: str) -> AuthSession | None:
    return await db.scalar(select(AuthSession).where(AuthSession.token_hash == token_hash))


async def revoke_session(db: AsyncSession, token_hash: str) -> None:
    await db.execute(update(AuthSession).where(AuthSession.token_hash == token_hash).values(revoked=True))
