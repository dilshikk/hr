from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.app.api.v1 import router
from backend.app.core.config import get_settings
from backend.app.core.logging import setup_logging
from backend.app.services.errors import ServiceError

settings = get_settings()
setup_logging(settings.log_level)

app = FastAPI(title="MADO HR Platform", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins,  # только свой домен Mini App / админ-панели
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
)


@app.exception_handler(ServiceError)
async def service_error_handler(_: Request, exc: ServiceError) -> JSONResponse:
    return JSONResponse(status_code=exc.status, content={"detail": exc.message})


app.include_router(router)


@app.get("/health/live")
async def live() -> dict:
    return {"status": "ok"}
