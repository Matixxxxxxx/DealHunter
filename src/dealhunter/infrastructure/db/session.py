"""Асинхронный движок SQLAlchemy и фабрика сессий.

Статья X Конституции («Производительность») требует, чтобы размер пула
соединений был конфигурируемым, а не захардкоженным — параметры берутся
из Settings.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from dealhunter.core.config import get_settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    """Возвращает singleton асинхронного движка БД для текущего процесса."""
    settings = get_settings()
    return create_async_engine(
        settings.database_url,
        echo=settings.db_echo,
        pool_size=settings.db_pool_size,
        max_overflow=settings.db_max_overflow,
        pool_pre_ping=True,
    )


@lru_cache(maxsize=1)
def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Возвращает singleton фабрики асинхронных сессий."""
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        autoflush=False,
    )


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI-зависимость: выдаёт сессию БД и гарантированно закрывает её.

    Использование:
        async def endpoint(session: AsyncSession = Depends(get_db_session)): ...
    """
    session_factory = get_session_factory()
    async with session_factory() as session:
        yield session
