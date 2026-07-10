"""Абстрактный интерфейс репозитория объявлений."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from dealhunter.domain.listings.entities import Listing


class ListingRepository(ABC):
    """Контракт хранилища объявлений."""

    @abstractmethod
    async def get_by_id(self, listing_id: UUID) -> Listing | None:
        """Возвращает объявление по внутреннему ID."""

    @abstractmethod
    async def get_by_source_and_external_id(
        self, source: str, external_id: str
    ) -> Listing | None:
        """Ищет объявление по паре (источник, внешний ID) — основа дедупликации.

        Уникальность именно по паре, а не только по external_id: разные
        источники вполне могут независимо использовать пересекающиеся
        идентификаторы (Том 8, раздел 8).
        """

    @abstractmethod
    async def create(self, listing: Listing) -> Listing:
        """Сохраняет новое объявление."""

    @abstractmethod
    async def update(self, listing: Listing) -> Listing:
        """Обновляет существующее объявление (например, при изменении цены)."""

    @abstractmethod
    async def list_by_source(self, source: str, limit: int = 100) -> list[Listing]:
        """Возвращает последние объявления конкретного источника."""
