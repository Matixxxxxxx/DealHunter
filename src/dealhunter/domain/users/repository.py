"""Абстрактный интерфейс репозитория пользователей.

Application-слой зависит только от этого интерфейса, а не от конкретной
реализации на SQLAlchemy — это и есть инверсия зависимостей (Статья VI
Конституции: «независимость компонентов»).
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from dealhunter.domain.users.entities import User


class UserRepository(ABC):
    """Контракт хранилища пользователей."""

    @abstractmethod
    async def get_by_id(self, user_id: UUID) -> User | None:
        """Возвращает пользователя по внутреннему ID или None, если не найден."""

    @abstractmethod
    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Возвращает пользователя по Telegram ID или None, если не найден."""

    @abstractmethod
    async def create(self, user: User) -> User:
        """Создаёт нового пользователя и возвращает сохранённую сущность."""

    @abstractmethod
    async def update(self, user: User) -> User:
        """Обновляет существующего пользователя и возвращает актуальную сущность."""
