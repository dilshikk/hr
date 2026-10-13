import asyncio
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.models import AuthSession, Base, User, utcnow
from app.tasks.cleanup import cleanup_expired_sessions


async def _run() -> list[str]:
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    now = utcnow()
    async with Session() as db:
        user = User(telegram_id=1)
        db.add(user)
        await db.flush()
        db.add_all([
            AuthSession(user_id=user.id, token_hash="active", expires_at=now + timedelta(hours=1)),
            AuthSession(user_id=user.id, token_hash="expired", expires_at=now - timedelta(minutes=1)),
            AuthSession(user_id=user.id, token_hash="revoked", expires_at=now + timedelta(hours=1), revoked=True),
        ])
        await db.commit()
        removed = await cleanup_expired_sessions(db, now=now)
        assert removed == 2
        left = (await db.scalars(select(AuthSession.token_hash))).all()
    await engine.dispose()
    return list(left)


def test_removes_only_expired_and_revoked():
    assert asyncio.run(_run()) == ["active"]
