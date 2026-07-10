"""Единый контракт коннектора источника данных.

Соответствует Тому 8 (Source Connectors & Data Collection), раздел 3:
Search Engine и остальная система работают только через этот интерфейс и
никогда не знают, что за площадка стоит за конкретной реализацией.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol

from dealhunter.domain.listings.entities import Listing


class ListingFetcher(Protocol):
    """Граница получения "сырых" данных — сознательно отделена от парсинга.

    Реализация этого протокола — это ответ на вопрос "откуда физически
    берутся данные" (официальный API, лицензированный фид, локальный файл
    для тестов, или прямой HTTP-запрос к площадке). Это решение имеет
    юридические последствия (Статья VII Конституции: соблюдение правил
    источников данных) и должно приниматься осознанно, отдельно от вопроса
    "как эти данные распарсить".
    """

    async def fetch_search_html(self, query: str) -> str:
        """Возвращает HTML страницы результатов поиска по запросу."""
        ...

    async def fetch_listing_html(self, external_id: str) -> str | None:
        """Возвращает HTML страницы конкретного объявления, если доступно."""
        ...


class SourceConnector(ABC):
    """Единый интерфейс коннектора — Том 8, раздел 3.

    Реализация обязана привести результат к внутренней модели `Listing`
    (Том 8, раздел 4) — вызывающий код (Search Engine) никогда не работает
    с "сырыми" данными источника напрямую.
    """

    source_name: str

    @abstractmethod
    async def initialize(self) -> None:
        """Инициализирует ресурсы коннектора (сессии, соединения и т.п.)."""

    @abstractmethod
    async def search(self, query: str) -> list[Listing]:
        """Ищет объявления по текстовому запросу, возвращает нормализованные Listing."""

    @abstractmethod
    async def fetch_listing(self, external_id: str) -> Listing | None:
        """Возвращает полную информацию по конкретному объявлению источника."""

    @abstractmethod
    async def health_check(self) -> bool:
        """Проверяет работоспособность коннектора (Том 8, раздел 12)."""

    @abstractmethod
    async def shutdown(self) -> None:
        """Освобождает ресурсы коннектора при остановке приложения."""
