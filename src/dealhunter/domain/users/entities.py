"""Доменные сущности пользователя.

Важно: этот модуль не импортирует ни SQLAlchemy, ни FastAPI, ни aiogram.
Это чистое ядро бизнес-логики (Clean Architecture) — оно не должно знать,
как сущность хранится или доставляется пользователю.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class UserRole(StrEnum):
    """Роли пользователей — Том 3 PRD, раздел 6."""

    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"


class SubscriptionTier(StrEnum):
    """Уровни подписки — Том 3 DDD, раздел 7 / Том 10 PRO Subscription."""

    FREE = "free"
    PRO = "pro"
    BUSINESS = "business"


@dataclass(frozen=True, slots=True)
class User:
    """Доменная сущность пользователя.

    Поля соответствуют таблице `Users` из Тома 3 (DDD), но без
    инфраструктурных деталей хранения (индексов, FK и т.п.).
    """

    id: UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    role: UserRole
    subscription_tier: SubscriptionTier
    language: str = "ru"
    is_active: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    @property
    def display_name(self) -> str:
        """Имя для отображения в интерфейсах (бот, веб)."""
        if self.username:
            return f"@{self.username}"
        return self.first_name or f"User#{self.telegram_id}"

    @property
    def is_pro_or_higher(self) -> bool:
        """Есть ли у пользователя доступ к PRO-функциям (Том 10)."""
        return self.subscription_tier in (SubscriptionTier.PRO, SubscriptionTier.BUSINESS)
