"""Health-check эндпоинт (Том 2 SAD, раздел 24: мониторинг).

Это простой liveness-check без обращения к БД/Redis — он должен отвечать
мгновенно и не падать из-за временной недоступности зависимостей.
Полноценный readiness-check (с проверкой БД/Redis) добавляется отдельной
задачей вместе с реальным Docker Compose окружением.
"""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    service: str


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Liveness-проверка: процесс запущен и отвечает на запросы."""
    return HealthResponse(status="ok", service="dealhunter-api")
