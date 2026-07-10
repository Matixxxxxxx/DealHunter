"""Реализация ListingRepository поверх SQLAlchemy 2.0 (async)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dealhunter.domain.listings.entities import Listing
from dealhunter.domain.listings.repository import ListingRepository
from dealhunter.infrastructure.db.models.listing import ListingModel


def _to_entity(model: ListingModel) -> Listing:
    return Listing(
        id=model.id,
        source=model.source,
        external_id=model.external_id,
        title=model.title,
        url=model.url,
        price_minor_units=model.price_minor_units,
        currency=model.currency,
        location=model.location,
        image_url=model.image_url,
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyListingRepository(ListingRepository):
    """Реализация репозитория объявлений поверх PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, listing_id: UUID) -> Listing | None:
        model = await self._session.get(ListingModel, listing_id)
        return _to_entity(model) if model else None

    async def get_by_source_and_external_id(
        self, source: str, external_id: str
    ) -> Listing | None:
        stmt = select(ListingModel).where(
            ListingModel.source == source, ListingModel.external_id == external_id
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, listing: Listing) -> Listing:
        model = ListingModel(
            id=listing.id,
            source=listing.source,
            external_id=listing.external_id,
            title=listing.title,
            url=listing.url,
            price_minor_units=listing.price_minor_units,
            currency=listing.currency,
            location=listing.location,
            image_url=listing.image_url,
            status=listing.status,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, listing: Listing) -> Listing:
        model = await self._session.get(ListingModel, listing.id)
        if model is None:
            raise ValueError(f"Объявление {listing.id} не найдено при обновлении")

        model.title = listing.title
        model.price_minor_units = listing.price_minor_units
        model.location = listing.location
        model.image_url = listing.image_url
        model.status = listing.status

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def list_by_source(self, source: str, limit: int = 100) -> list[Listing]:
        stmt = (
            select(ListingModel)
            .where(ListingModel.source == source)
            .order_by(ListingModel.created_at.desc())
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return [_to_entity(model) for model in result.scalars().all()]
