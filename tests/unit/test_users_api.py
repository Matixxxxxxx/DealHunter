"""Юнит-тесты REST-эндпоинтов пользователей.

По аналогии с `test_register_user_use_case.py`: используется in-memory
fake-репозиторий вместо реальной БД. Use case подменяется через
`app.dependency_overrides` — presentation-слой тестируется изолированно,
без поднятия PostgreSQL (интеграционные тесты с реальной БД — отдельная
задача, см. `tests/integration/`).
"""

from __future__ import annotations

from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from dealhunter.application.users.use_cases import GetUserProfileUseCase, RegisterUserUseCase
from dealhunter.domain.users.entities import User
from dealhunter.domain.users.repository import UserRepository
from dealhunter.presentation.api.app import create_app
from dealhunter.presentation.api.dependencies import (
    get_register_user_use_case,
    get_user_profile_use_case,
)


class FakeUserRepository(UserRepository):
    """In-memory реализация UserRepository для юнит-тестов API-слоя."""

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


@pytest.fixture
def client() -> TestClient:
    app = create_app()
    repository = FakeUserRepository()

    app.dependency_overrides[get_register_user_use_case] = lambda: RegisterUserUseCase(
        user_repository=repository
    )
    app.dependency_overrides[get_user_profile_use_case] = lambda: GetUserProfileUseCase(
        user_repository=repository
    )

    return TestClient(app)


def test_register_user_returns_created_user(client: TestClient) -> None:
    response = client.post(
        "/api/v1/users/register",
        json={"telegram_id": 123456789, "username": "test_user", "language": "ru"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["telegram_id"] == 123456789
    assert body["display_name"] == "@test_user"
    assert body["is_pro_or_higher"] is False


def test_register_user_is_idempotent(client: TestClient) -> None:
    first = client.post("/api/v1/users/register", json={"telegram_id": 42, "language": "ru"})
    second = client.post("/api/v1/users/register", json={"telegram_id": 42, "language": "ru"})

    assert first.json()["id"] == second.json()["id"]


def test_get_user_profile_returns_registered_user(client: TestClient) -> None:
    created = client.post(
        "/api/v1/users/register", json={"telegram_id": 777, "language": "ru"}
    ).json()

    response = client.get(f"/api/v1/users/{created['id']}")

    assert response.status_code == 200
    assert response.json()["telegram_id"] == 777


def test_get_user_profile_returns_404_for_unknown_id(client: TestClient) -> None:
    response = client.get("/api/v1/users/00000000-0000-0000-0000-000000000000")

    assert response.status_code == 404
