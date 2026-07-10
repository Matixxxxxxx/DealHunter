"""Асинхронный клиент Redis.

Используется как: кэш справочников, хранилище FSM Telegram-бота, очереди,
rate limiting (Том 2 SAD, раздел 18).
"""

from __future__ import annotations

from functools import lru_cache
from typing import cast

from redis.asyncio import Redis

from dealhunter.core.config import get_settings


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:
    """Возвращает singleton асинхронного клиента Redis для текущего процесса."""
    settings = get_settings()
    # Redis.from_url возвращает объект, который мы приводим к типу Redis
    client = Redis.from_url(settings.redis_url, decode_responses=True)
    return cast(Redis, client)
