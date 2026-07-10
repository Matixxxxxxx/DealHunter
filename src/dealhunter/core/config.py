"""Централизованная конфигурация приложения.

Согласно Статье IV DealHunter AI Constitution («Конфигурируемость»), все
параметры окружения читаются один раз через Pydantic Settings и нигде
больше не должны хардкодиться в коде.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["local", "staging", "production"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseSettings):
    """Настройки приложения, читаемые из переменных окружения / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    # --- Общие ---
    environment: Environment = "local"
    log_level: LogLevel = "INFO"
    secret_key: str = Field(..., min_length=8)

    # --- API ---
    api_host: str = "0.0.0.0"
    api_port: int = 8000

    # --- База данных ---
    database_url: str = Field(
        ...,
        description="Async SQLAlchemy DSN, например postgresql+asyncpg://user:pass@host:5432/db",
    )
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_echo: bool = False

    # --- Redis ---
    redis_url: str = Field(..., description="redis://host:port/db")

    # --- Telegram Bot ---
    bot_token: str = Field(..., min_length=1)

    @property
    def is_production(self) -> bool:
        return self.environment == "production"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Возвращает закэшированный singleton настроек.

    lru_cache гарантирует, что .env читается один раз за время жизни
    процесса — важно для производительности и предсказуемости конфигурации.
    """
    return Settings()
