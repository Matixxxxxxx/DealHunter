"""Реализация UserRepository поверх SQLAlchemy 2.0 (async)."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from dealhunter.domain.users.entities import User
from dealhunter.domain.users.repository import UserRepository
from dealhunter.infrastructure.db.models.user import UserModel


def _to_entity(model: UserModel) -> User:
    """Преобразует ORM-модель в доменную сущность."""
    return User(
        id=model.id,
        telegram_id=model.telegram_id,
        username=model.username,
        first_name=model.first_name,
        last_name=model.last_name,
        role=model.role,
        subscription_tier=model.subscription_tier,
        language=model.language,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


class SQLAlchemyUserRepository(UserRepository):
    """Реализация репозитория пользователей поверх PostgreSQL."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: UUID) -> User | None:
        model = await self._session.get(UserModel, user_id)
        return _to_entity(model) if model else None

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        stmt = select(UserModel).where(UserModel.telegram_id == telegram_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return _to_entity(model) if model else None

    async def create(self, user: User) -> User:
        model = UserModel(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
            subscription_tier=user.subscription_tier,
            language=user.language,
            is_active=user.is_active,
        )
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)

    async def update(self, user: User) -> User:
        model = await self._session.get(UserModel, user.id)
        if model is None:
            raise ValueError(f"Пользователь {user.id} не найден при обновлении")

        model.username = user.username
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.role = user.role
        model.subscription_tier = user.subscription_tier
        model.language = user.language
        model.is_active = user.is_active

        await self._session.commit()
        await self._session.refresh(model)
        return _to_entity(model)
