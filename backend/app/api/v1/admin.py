"""Администрирование: журнал действий, настройки (заготовка)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])
