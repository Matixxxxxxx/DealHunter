"""Доменные сущности поискового профиля.

Соответствует таблицам `SearchProfiles` и `SearchFilters` из Тома 3 (DDD)
и режимам «Охотник / Снайпер / Перекупщик» из Тома 1 (PRD, раздел 9).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID


class SearchMode(StrEnum):
    """Режимы поиска — Том 1 PRD, раздел 9."""

    HUNTER = "hunter"      # Охотник — максимальная скорость, минимум фильтрации
    SNIPER = "sniper"      # Снайпер — строгие фильтры, максимальная точность
    RESELLER = "reseller"  # Перекупщик — приоритет прибыльных сделок


class Condition(StrEnum):
    """Состояние товара."""

    ANY = "any"
    NEW = "new"
    USED = "used"


class SellerType(StrEnum):
    """Тип продавца."""

    ANY = "any"
    PRIVATE = "private"
    COMPANY = "company"


@dataclass(frozen=True, slots=True)
class SearchFilters:
    """Фильтры поиска."""

    categories: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()

    # Цены храним как int (копейки), так как это финансовые данные
    price_min: int | None = None
    price_max: int | None = None

    condition: Condition = Condition.ANY
    seller_type: SellerType = SellerType.ANY
    exclude_words: tuple[str, ...] = ()
    required_words: tuple[str, ...] = ()

    # --- Только для режима "Перекупщик" ---
    min_profit: int | None = None      # Копейки
    min_liquidity: int | None = None   # Например, целое число (кол-во сделок)
    min_deal_score: int | None = None  # Например, целое число

    # Риски и уверенность — это коэффициенты (0.0 - 1.0), они требуют float
    max_risk: float | None = None
    min_confidence: float | None = None


@dataclass(frozen=True, slots=True)
class SearchProfile:
    """Доменная сущность поискового профиля — Том 3 DDD, раздел 8."""

    id: UUID
    user_id: UUID
    name: str
    mode: SearchMode
    filters: SearchFilters
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def requires_profit_criteria(self) -> bool:
        """Является ли профиль режимом "Перекупщик" с заданными критериями прибыли."""
        return self.mode is SearchMode.RESELLER and self.filters.min_profit is not None
