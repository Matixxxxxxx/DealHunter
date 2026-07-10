"""Общие фикстуры pytest.

На этом этапе (Задача №1 — скелет проекта) фикстуры БД/Redis ещё не
нужны: юнит-тесты покрывают только код, не требующий внешних сервисов.
Фикстуры для интеграционных тестов (реальная тестовая БД в Docker)
добавляются вместе с первыми репозиторными тестами.
"""

from __future__ import annotations

import os

import pytest

# Тестовое окружение задаётся здесь, а не через .env, чтобы `pytest` можно
# было запустить в CI без реального .env-файла.
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379/0")
os.environ.setdefault("BOT_TOKEN", "123456:TEST-TOKEN")


@pytest.fixture(autouse=True)
def _clear_settings_cache() -> None:
    """Сбрасывает lru_cache настроек между тестами, если они его меняют."""
    from dealhunter.core.config import get_settings

    get_settings.cache_clear()
