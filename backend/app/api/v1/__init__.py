from fastapi import APIRouter

from backend.app.api.v1 import admin, auth, branches, candidates, employees, interviews, reports, vacancies

router = APIRouter(prefix="/api/v1")
for module in (auth, candidates, vacancies, branches, interviews, employees, admin, reports):
    router.include_router(module.router)
