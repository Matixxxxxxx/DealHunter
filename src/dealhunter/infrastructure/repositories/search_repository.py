"""Реализация SearchProfileRepository поверх SQLAlchemy 2.0 (async)."""

from __future__ import annotations

from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dealhunter.domain.search.entities import Condition, SearchFilters, SearchProfile, SellerType
from dealhunter.domain.search.repository import SearchProfileRepository
from dealhunter.infrastructure.db.models.search_profile import SearchProfileModel


def _filters_to_dict(filters: SearchFilters) -> dict[str, object]:
    return {
        "categories": list(filters.categories),
        "regions": list(filters.regions),
        "price_min": filters.price_min,
        "price_max": filters.price_max,
        "condition": filters.condition.value,
        "seller_type": filters.seller_type.value,
        "exclude_words": list(filters.exclude_words),
        "required_words": list(filters.required_words),
        "min_profit": filters.min_profit,
        "min_liquidity": filters.min_liquidity,
        "min_deal_score": filters.min_deal_score,
        "max_risk": filters.max_risk,
        "min_confidence": filters.min_confidence,
    }


def _filters_from_dict(data: dict[str, object]) -> SearchFilters:
    # Безопасно извлекаем значения для Enum
    raw_condition = data.get("condition")
    raw_seller_type = data.get("seller_type")

    return SearchFilters(
        categories=tuple(cast(list[str], data.get("categories") or [])),
        regions=tuple(cast(list[str], data.get("regions") or [])),

        # Финансы — целые числа (копейки)
        price_min=cast(int | None, data.get("price_min")),
        price_max=cast(int | None, data.get("price_max")),

        # Enum приводим к строкам
        condition=Condition(str(raw_condition) if raw_condition else Condition.ANY.value),
        seller_type=SellerType(str(raw_seller_type) if raw_seller_type else SellerType.ANY.value),

        exclude_words=tuple(cast(list[str], data.get("exclude_words") or [])),
        required_words=tuple(cast(list[str], data.get("required_words") or [])),

        min_profit=cast(int | None, data.get("min_profit")),
        min_liquidity=cast(int | None, data.get("min_liquidity")),
        min_deal_score=cast(int | None, data.get("min_deal_score")),

        # Коэффициенты — дробные числа
        max_risk=cast(float | None, data.get("max_risk")),
        min_confidence=cast(float | None, data.get("min_confidence")),
    )


def _to_entity(model: SearchProfileModel) -> SearchProfile:
    return SearchProfile(
        id=model.id,
        user_id=model.user_id,
        name=model.name,
        mode=model.mode,
        filters=_filters_from_dict(model.filters),
        enabled=model.enabled,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemySearchProfileRepository(SearchProfileRepository):
    """Реализация репозитория поисковых профилей поверх PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, profile_id: UUID) -> SearchProfile | None:
        model = await self._session.get(SearchProfileModel, profile_id)
        return _to_entity(model) if model else None

    async def list_by_user(self, user_id: UUID) -> list[SearchProfile]:
        stmt = select(SearchProfileModel).where(SearchProfileModel.user_id == user_id)
        result = await self._session.execute(stmt)
        return [_to_entity(model) for model in result.scalars().all()]

    async def create(self, profile: SearchProfile) -> SearchProfile:
        model = SearchProfileModel(
            id=profile.id,
            user_id=profile.user_id,
            name=profile.name,
            mode=profile.mode,
            filters=_filters_to_dict(profile.filters),
            enabled=profile.enabled,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, profile: SearchProfile) -> SearchProfile:
        model = await self._session.get(SearchProfileModel, profile.id)
        if model is None:
            raise ValueError(f"Поисковый профиль {profile.id} не найден при обновлении")

        model.name = profile.name
        model.mode = profile.mode
        model.filters = _filters_to_dict(profile.filters)
        model.enabled = profile.enabled

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def delete(self, profile_id: UUID) -> None:
        model = await self._session.get(SearchProfileModel, profile_id)
        if model is not None:
            await self._session.delete(model)
            await self._session.commit()
