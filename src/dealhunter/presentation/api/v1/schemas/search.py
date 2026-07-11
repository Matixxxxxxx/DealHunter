"""Pydantic-схемы REST API поисковых профилей.

`SearchFiltersSchema` — зеркало `domain.search.entities.SearchFilters`,
конвертируется в обе стороны. Дублирование полей осознанное: это граница
между HTTP-контрактом и доменной моделью (Статья VI), они не обязаны
меняться синхронно.
"""

from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field

from dealhunter.domain.search.entities import (
    Condition,
    SearchFilters,
    SearchMode,
    SearchProfile,
    SellerType,
)


class SearchFiltersSchema(BaseModel):
    """DTO фильтров поиска."""

    categories: tuple[str, ...] = ()
    regions: tuple[str, ...] = ()

    price_min: int | None = None
    price_max: int | None = None

    condition: Condition = Condition.ANY
    seller_type: SellerType = SellerType.ANY
    exclude_words: tuple[str, ...] = ()
    required_words: tuple[str, ...] = ()

    min_profit: int | None = None
    min_liquidity: int | None = None
    min_deal_score: int | None = None

    max_risk: float | None = None
    min_confidence: float | None = None

    def to_domain(self) -> SearchFilters:
        return SearchFilters(**self.model_dump())

    @classmethod
    def from_domain(cls, filters: SearchFilters) -> SearchFiltersSchema:
        return cls(
            categories=filters.categories,
            regions=filters.regions,
            price_min=filters.price_min,
            price_max=filters.price_max,
            condition=filters.condition,
            seller_type=filters.seller_type,
            exclude_words=filters.exclude_words,
            required_words=filters.required_words,
            min_profit=filters.min_profit,
            min_liquidity=filters.min_liquidity,
            min_deal_score=filters.min_deal_score,
            max_risk=filters.max_risk,
            min_confidence=filters.min_confidence,
        )


class CreateSearchProfileRequest(BaseModel):
    """Тело запроса создания поискового профиля (мастер из Тома 1 PRD, раздел 6)."""

    user_id: UUID
    name: str = Field(min_length=1, max_length=256)
    mode: SearchMode
    filters: SearchFiltersSchema = SearchFiltersSchema()


class SearchProfileResponse(BaseModel):
    """Публичное представление поискового профиля."""

    id: UUID
    user_id: UUID
    name: str
    mode: SearchMode
    filters: SearchFiltersSchema
    enabled: bool

    @classmethod
    def from_entity(cls, profile: SearchProfile) -> SearchProfileResponse:
        return cls(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            mode=profile.mode,
            filters=SearchFiltersSchema.from_domain(profile.filters),
            enabled=profile.enabled,
        )
