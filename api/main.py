from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import auth, candidates, vacancies
from config import get_settings

app = FastAPI(title="MADO HR Platform", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().origins,  # только свой домен Mini App
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(auth.router)
app.include_router(candidates.router)
app.include_router(vacancies.router)


@app.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}
