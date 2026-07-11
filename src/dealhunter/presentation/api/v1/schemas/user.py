"""Pydantic-схемы REST API пользователей.

Отделены от доменной сущности `User` намеренно: presentation-слой не должен
навязывать domain'у формат HTTP-представления, и наоборот (Статья VI
Конституции — независимость компонентов).
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from dealhunter.domain.users.entities import SubscriptionTier, User, UserRole


class RegisterUserRequest(BaseModel):
    """Тело запроса регистрации — идемпотентно по `telegram_id`.

    Используется как ботом (при `/start`), так и напрямую через API.
    """

    telegram_id: int
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    language: str = Field(default="ru", min_length=2, max_length=8)


class UserResponse(BaseModel):
    """Публичное представление пользователя."""

    id: UUID
    telegram_id: int
    username: str | None
    first_name: str | None
    last_name: str | None
    display_name: str
    role: UserRole
    subscription_tier: SubscriptionTier
    is_pro_or_higher: bool
    language: str
    is_active: bool

    @classmethod
    def from_entity(cls, user: User) -> UserResponse:
        return cls(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            display_name=user.display_name,
            role=user.role,
            subscription_tier=user.subscription_tier,
            is_pro_or_higher=user.is_pro_or_higher,
            language=user.language,
            is_active=user.is_active,
        )
