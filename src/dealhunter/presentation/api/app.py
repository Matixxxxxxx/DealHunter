"""Фабрика FastAPI-приложения — API Gateway (Том 2 SAD, раздел 5).

На старте проекта Gateway и бизнес-эндпоинты живут в одном процессе
(модульный монолит). Функции Gateway (авторизация, rate limit, роутинг),
описанные в Томе 2, добавляются инкрементально последующими задачами.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from dealhunter.core.config import get_settings
from dealhunter.core.exceptions import (
    ConflictError,
    DealHunterError,
    NotFoundError,
    PermissionDeniedError,
    ValidationError,
)
from dealhunter.core.logging import configure_logging, get_logger
from dealhunter.infrastructure.db.session import get_engine
from dealhunter.presentation.api.v1.routers import health, search, users

logger = get_logger(__name__)

_EXCEPTION_STATUS_MAP: dict[type[DealHunterError], int] = {
    NotFoundError: 404,
    ValidationError: 422,
    ConflictError: 409,
    PermissionDeniedError: 403,
}


@asynccontextmanager
async def _lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Управляет ресурсами уровня процесса (движок БД) на старте/остановке."""
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("DealHunter API стартует (environment=%s)", settings.environment)

    yield

    logger.info("DealHunter API останавливается — закрываю соединения с БД")
    await get_engine().dispose()


def create_app() -> FastAPI:
    """Создаёт и конфигурирует экземпляр FastAPI-приложения."""
    app = FastAPI(
        title="DealHunter AI API",
        version="0.1.0",
        lifespan=_lifespan,
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(users.router, prefix="/api/v1")
    app.include_router(search.router, prefix="/api/v1")

    @app.exception_handler(DealHunterError)
    async def handle_domain_error(request: Request, exc: DealHunterError) -> JSONResponse:
        """Транслирует доменные исключения в корректные HTTP-статусы."""
        status_code = _EXCEPTION_STATUS_MAP.get(type(exc), 400)
        return JSONResponse(status_code=status_code, content={"detail": str(exc)})

    return app
