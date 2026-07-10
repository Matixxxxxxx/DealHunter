"""Абстрактный интерфейс репозитория поисковых профилей."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from dealhunter.domain.search.entities import SearchProfile


class SearchProfileRepository(ABC):
    """Контракт хранилища поисковых профилей."""

    @abstractmethod
    async def get_by_id(self, profile_id: UUID) -> SearchProfile | None:
        """Возвращает поисковый профиль по ID или None, если не найден."""

    @abstractmethod
    async def list_by_user(self, user_id: UUID) -> list[SearchProfile]:
        """Возвращает все поисковые профили пользователя."""

    @abstractmethod
    async def create(self, profile: SearchProfile) -> SearchProfile:
        """Создаёт новый поисковый профиль."""

    @abstractmethod
    async def update(self, profile: SearchProfile) -> SearchProfile:
        """Обновляет существующий поисковый профиль."""

    @abstractmethod
    async def delete(self, profile_id: UUID) -> None:
        """Удаляет поисковый профиль."""
