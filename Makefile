.PHONY: help install run-api run-bot run-worker migrate migrate-generate \
        test test-cov lint format typecheck check docker-up docker-down \
        docker-build docker-logs

help:
	@echo "DealHunter AI — доступные команды:"
	@echo "  make install          — установить зависимости через Poetry"
	@echo "  make run-api          — запустить API локально (uvicorn --reload)"
	@echo "  make run-bot          — запустить Telegram-бота локально"
	@echo "  make run-worker       — запустить фоновый воркер локально"
	@echo "  make migrate          — применить миграции Alembic"
	@echo "  make migrate-generate m=\"описание\" — сгенерировать новую миграцию"
	@echo "  make test             — запустить тесты"
	@echo "  make test-cov         — запустить тесты с отчётом покрытия"
	@echo "  make lint             — проверить код Ruff"
	@echo "  make format           — отформатировать код Black + Ruff"
	@echo "  make typecheck        — проверить типы MyPy"
	@echo "  make check            — lint + typecheck + test (как в CI)"
	@echo "  make docker-up        — поднять всё окружение в Docker Compose"
	@echo "  make docker-down      — остановить окружение"
	@echo "  make docker-build     — пересобрать образы"
	@echo "  make docker-logs      — логи всех сервисов"

install:
	poetry install

run-api:
	poetry run uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000

run-bot:
	poetry run python -m apps.bot.main

run-worker:
	poetry run python -m apps.worker.main

migrate:
	poetry run alembic upgrade head

migrate-generate:
	poetry run alembic revision --autogenerate -m "$(m)"

test:
	poetry run pytest

test-cov:
	poetry run pytest --cov=dealhunter --cov-report=html

lint:
	poetry run ruff check .

format:
	poetry run black .
	poetry run ruff check --fix .

typecheck:
	poetry run mypy src

check: lint typecheck test

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

docker-build:
	docker compose build --no-cache

docker-logs:
	docker compose logs -f
