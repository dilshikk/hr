"""Сотрудники: назначение ролей и филиалов (заготовка)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/employees", tags=["employees"])
