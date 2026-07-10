# DealHunter AI

Интеллектуальная платформа анализа вторичного рынка и поиска выгодных
предложений на онлайн-площадках объявлений.

Полная проектная документация (17 томов — Vision, PRD, Architecture,
Database Design, AI Engine, Search Engine и т.д.) и обязательный свод
архитектурных принципов находятся в `ARCHITECTURE_PRINCIPLES.md` — **этот
файл должен быть прочитан перед любым изменением кода.**

---

## Стек технологий

| Слой            | Технология                          |
|------------------|--------------------------------------|
| Язык             | Python 3.13                          |
| API              | FastAPI + Uvicorn                    |
| Telegram-клиент  | aiogram 3                            |
| БД               | PostgreSQL 17, SQLAlchemy 2.0 (async)|
| Миграции         | Alembic (async)                      |
| Кэш / очереди / FSM | Redis                             |
| Контейнеризация  | Docker, Docker Compose               |
| Тесты            | Pytest, pytest-asyncio               |
| Форматирование   | Black, Ruff                          |
| Типизация        | MyPy (strict)                        |
| Управление зависимостями | Poetry                        |

---

## Архитектура

Проект построен как **модульный монолит** по правилам Clean Architecture
(это осознанный старт согласно Тому 2 SAD — сервисы выделяются позже без
переписывания бизнес-логики). Зависимости слоёв направлены только внутрь:

```
presentation  →  application  →  domain
                                    ↑
infrastructure ────────────────────┘
      (реализует интерфейсы domain, но domain о ней не знает)
```

- **`src/dealhunter/domain/`** — чистые бизнес-сущности (dataclasses) и
  абстрактные интерфейсы репозиториев. Никаких импортов FastAPI /
  SQLAlchemy / aiogram — это ядро, независимое от фреймворков.
- **`src/dealhunter/application/`** — use cases, оркестрируют domain через
  абстракции репозиториев (Dependency Inversion).
- **`src/dealhunter/infrastructure/`** — SQLAlchemy-модели, реализации
  репозиториев, Redis-клиент.
- **`src/dealhunter/presentation/`** — тонкие адаптеры: FastAPI (`api/`) и
  aiogram (`bot/`).
- **`apps/`** — точки входа отдельных процессов: `api`, `bot`, `worker`
  (каждый — свой Docker-контейнер, Том 2 SAD раздел 22).
- **`migrations/`** — асинхронные миграции Alembic.
- **`tests/`** — `unit/` (без внешних зависимостей, на fake-репозиториях)
  и `integration/` (с реальной БД, добавляются по мере реализации).

Сейчас реализован полный вертикальный срез на двух bounded context'ах —
**users** и **search** — как эталон структуры. Остальные ~28 таблиц и
сервисы из Тома 3 (DDD) и Тома 2 (SAD) добавляются последующими задачами
по той же схеме.

---

## Быстрый старт (локально, без Docker)

```bash
# 1. Установить зависимости
poetry install

# 2. Настроить окружение
cp .env.example .env
# отредактировать .env: DATABASE_URL, REDIS_URL, BOT_TOKEN, SECRET_KEY

# 3. Поднять PostgreSQL и Redis (например, через Docker)
docker compose up -d db redis

# 4. Применить миграции
make migrate

# 5. Запустить API
make run-api

# 6. Запустить бота (в отдельном терминале)
make run-bot
```

## Быстрый старт (полностью в Docker)

```bash
cp .env.example .env
make docker-up
```

Это поднимет `db`, `redis`, `api`, `bot`, `worker`. API будет доступен на
`http://localhost:8000/api/v1/health`.

---

## Разработка

```bash
make test          # тесты
make test-cov      # тесты с отчётом покрытия (htmlcov/)
make lint          # Ruff
make format        # Black + Ruff --fix
make typecheck     # MyPy (strict)
make check         # всё вместе, как в CI
```

### Миграции

```bash
make migrate-generate m="add listings table"
make migrate
```

---

## Структура репозитория

См. дерево проекта в конце вывода последней задачи по инициализации
репозитория, либо `find . -type f` из корня проекта.

---

## Обязательные принципы разработки

Перед началом работы над любой задачей — **обязательно** ознакомьтесь с
[`ARCHITECTURE_PRINCIPLES.md`](./ARCHITECTURE_PRINCIPLES.md). Он определяет
20 статей, обязательных для любого разработчика или AI-инструмента,
работающего над этим репозиторием (включая Codex/Claude).

Ключевые из них, влияющие на повседневную разработку:

- Все веса, лимиты и пороги — в конфигурации, никогда не в коде (Статья IV).
- Новый источник данных / категория / аналитика — отдельный модуль, ядро
  не переписывается (Статья V).
- Любое изменение схемы БД или API — через миграцию и документацию
  (Статья IX).
- AI-оценки всегда объяснимы и сопровождаются уровнем уверенности
  (Статьи II, III, XVII).
