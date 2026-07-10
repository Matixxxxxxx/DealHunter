"""Юнит-тест RegisterUserUseCase на in-memory fake-репозитории.

Демонстрирует ключевое преимущество Clean Architecture: бизнес-логика
тестируется без реальной БД — достаточно реализовать абстрактный
интерфейс UserRepository.
"""

from __future__ import annotations

from uuid import UUID

import pytest

from dealhunter.application.users.use_cases import RegisterUserUseCase
from dealhunter.domain.users.entities import User
from dealhunter.domain.users.repository import UserRepository


class FakeUserRepository(UserRepository):
    """In-memory реализация UserRepository для юнит-тестов."""

    def __init__(self) -> None:
        self._users: dict[UUID, User] = {}

    async def get_by_id(self, user_id: UUID) -> User | None:
        return self._users.get(user_id)

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        for user in self._users.values():
            if user.telegram_id == telegram_id:
                return user
        return None

    async def create(self, user: User) -> User:
        self._users[user.id] = user
        return user

    async def update(self, user: User) -> User:
        self._users[user.id] = user
        return user


@pytest.mark.asyncio
async def test_register_user_creates_new_user() -> None:
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(user_repository=repository)

    user = await use_case.execute(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
        last_name=None,
    )

    assert user.telegram_id == 123456789
    assert user.display_name == "@test_user"
    assert user.is_pro_or_higher is False


@pytest.mark.asyncio
async def test_register_user_is_idempotent() -> None:
    repository = FakeUserRepository()
    use_case = RegisterUserUseCase(user_repository=repository)

    first_call = await use_case.execute(
        telegram_id=42, username=None, first_name="Alex", last_name=None
    )
    second_call = await use_case.execute(
        telegram_id=42, username=None, first_name="Alex", last_name=None
    )

    assert first_call.id == second_call.id
