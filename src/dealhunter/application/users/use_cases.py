"""Use cases уровня приложения для пользователей.

Use case — единственная точка входа в бизнес-логику для конкретного
сценария. Presentation-слой (API, бот) вызывает use case и не содержит
бизнес-правил самостоятельно.
"""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from dealhunter.core.exceptions import NotFoundError
from dealhunter.domain.users.entities import SubscriptionTier, User, UserRole
from dealhunter.domain.users.repository import UserRepository


@dataclass(slots=True)
class RegisterUserUseCase:
    """Регистрирует нового пользователя при первом /start в боте.

    Если пользователь с таким telegram_id уже существует — возвращает его
    без изменений (идемпотентная операция).
    """

    user_repository: UserRepository

    async def execute(
        self,
        *,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        language: str = "ru",
    ) -> User:
        existing = await self.user_repository.get_by_telegram_id(telegram_id)
        if existing is not None:
            return existing

        new_user = User(
            id=uuid4(),
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=UserRole.USER,
            subscription_tier=SubscriptionTier.FREE,
            language=language,
        )
        return await self.user_repository.create(new_user)


@dataclass(slots=True)
class GetUserProfileUseCase:
    """Возвращает профиль пользователя по внутреннему ID."""

    user_repository: UserRepository

    async def execute(self, user_id: UUID) -> User:
        user = await self.user_repository.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Пользователь {user_id} не найден")
        return user
