"""Use cases уровня приложения для поисковых профилей."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

from dealhunter.core.exceptions import NotFoundError, PermissionDeniedError
from dealhunter.domain.search.entities import SearchFilters, SearchMode, SearchProfile
from dealhunter.domain.search.repository import SearchProfileRepository


@dataclass(slots=True)
class CreateSearchProfileUseCase:
    """Создаёт новый поисковый профиль — соответствует мастеру из Тома 1, раздел 6."""

    search_repository: SearchProfileRepository

    async def execute(
        self,
        *,
        user_id: UUID,
        name: str,
        mode: SearchMode,
        filters: SearchFilters,
    ) -> SearchProfile:
        profile = SearchProfile(
            id=uuid4(),
            user_id=user_id,
            name=name,
            mode=mode,
            filters=filters,
        )
        return await self.search_repository.create(profile)


@dataclass(slots=True)
class ListUserSearchesUseCase:
    """Возвращает все поисковые профили пользователя — раздел "Мои поиски"."""

    search_repository: SearchProfileRepository

    async def execute(self, user_id: UUID) -> list[SearchProfile]:
        return await self.search_repository.list_by_user(user_id)


@dataclass(slots=True)
class DeleteSearchProfileUseCase:
    """Удаляет поисковый профиль, только если он принадлежит указанному пользователю."""

    search_repository: SearchProfileRepository

    async def execute(self, *, user_id: UUID, profile_id: UUID) -> None:
        profile = await self.search_repository.get_by_id(profile_id)
        if profile is None:
            raise NotFoundError(f"Поисковый профиль {profile_id} не найден")
        if profile.user_id != user_id:
            raise PermissionDeniedError("Профиль принадлежит другому пользователю")
        await self.search_repository.delete(profile_id)
