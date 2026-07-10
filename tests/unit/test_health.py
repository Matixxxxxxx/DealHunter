"""Юнит-тест health-check эндпоинта."""

from __future__ import annotations

from fastapi.testclient import TestClient

from dealhunter.presentation.api.app import create_app


def test_health_check_returns_ok() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "dealhunter-api"}
