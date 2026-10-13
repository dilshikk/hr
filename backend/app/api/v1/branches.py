"""Филиалы (заготовка)."""
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/branches", tags=["branches"])
