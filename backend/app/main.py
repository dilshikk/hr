import asyncio
import contextlib
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin, auth, branches, candidates, dashboard, employees, interviews, reports, vacancies
from app.core.config import get_settings
from app.core.logging import setup_logging
from app.tasks.cleanup import run_cleanup_loop

setup_logging()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    task = asyncio.create_task(run_cleanup_loop())
    try:
        yield
    finally:
        task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await task


app = FastAPI(title="MADO HR Platform", docs_url=None, redoc_url=None, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,  # только свой домен Mini App
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

for module in (auth, candidates, vacancies, interviews, employees, branches, admin, reports, dashboard):
    app.include_router(module.router)


@app.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}
