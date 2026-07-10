"""FastAPI dependency-провайдеры.

Здесь и только здесь presentation-слой "знает" о конкретных реализациях
репозиториев — use cases получают уже готовые абстракции через DI.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from dealhunter.application.search.use_cases import (
    CreateSearchProfileUseCase,
    DeleteSearchProfileUseCase,
    ListUserSearchesUseCase,
)
from dealhunter.application.users.use_cases import GetUserProfileUseCase, RegisterUserUseCase
from dealhunter.infrastructure.db.session import get_db_session
from dealhunter.infrastructure.repositories.search_repository import (
    SQLAlchemySearchProfileRepository,
)
from dealhunter.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

DbSession = Annotated[AsyncSession, Depends(get_db_session)]


def get_register_user_use_case(session: DbSession) -> RegisterUserUseCase:
    return RegisterUserUseCase(user_repository=SQLAlchemyUserRepository(session))


def get_user_profile_use_case(session: DbSession) -> GetUserProfileUseCase:
    return GetUserProfileUseCase(user_repository=SQLAlchemyUserRepository(session))


def get_create_search_profile_use_case(session: DbSession) -> CreateSearchProfileUseCase:
    return CreateSearchProfileUseCase(
        search_repository=SQLAlchemySearchProfileRepository(session)
    )


def get_list_user_searches_use_case(session: DbSession) -> ListUserSearchesUseCase:
    return ListUserSearchesUseCase(search_repository=SQLAlchemySearchProfileRepository(session))


def get_delete_search_profile_use_case(session: DbSession) -> DeleteSearchProfileUseCase:
    return DeleteSearchProfileUseCase(
        search_repository=SQLAlchemySearchProfileRepository(session)
    )
