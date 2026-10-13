from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import admin, auth, branches, candidates, employees, interviews, reports, vacancies
from app.core.config import get_settings
from app.core.logging import setup_logging

setup_logging()

app = FastAPI(title="MADO HR Platform", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,  # только свой домен Mini App
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

for module in (auth, candidates, vacancies, interviews, employees, branches, admin, reports):
    app.include_router(module.router)


@app.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}
