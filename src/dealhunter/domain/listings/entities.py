"""Доменная сущность объявления.

Объединяет функциональность `Listings` и `Product` из более ранних
прототипов в одну сущность — по Тому 3 (DDD) объявление должно быть одной
таблицей, а не дублироваться под разными именами с разными наборами полей.

Денежные значения хранятся в минимальных единицах валюты (копейках) —
Том 3 DDD, раздел 3, тот же принцип уже используется в
`domain.search.entities.SearchFilters`.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class ListingStatus(StrEnum):
    """Статус объявления на источнике."""

    ACTIVE = "active"
    REMOVED = "removed"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Listing:
    """Внутренняя (нормализованная) модель объявления — Том 8, раздел 4.

    Не содержит ничего специфичного для конкретного источника — это и есть
    "Internal Listing Model", к которой приводят данные все коннекторы.
    """

    id: UUID
    source: str  # например "avito" — имя коннектора-источника
    external_id: str  # идентификатор объявления на стороне источника
    title: str
    url: str
    price_minor_units: int | None  # цена в копейках; None — цена не указана
    currency: str = "RUB"
    location: str | None = None
    image_url: str | None = None
    status: ListingStatus = ListingStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    @property
    def price_display(self) -> str | None:
        """Цена в основной единице валюты (рубли), для отображения пользователю."""
        if self.price_minor_units is None:
            return None
        return f"{self.price_minor_units / 100:,.0f}".replace(",", " ")
