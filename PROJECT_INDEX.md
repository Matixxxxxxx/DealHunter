# PROJECT_INDEX — DealHunter AI

> Автоматически поддерживаемая техническая карта проекта.
> Источник архитектурных правил: `ARCHITECTURE_PRINCIPLES.md` («DealHunter AI Constitution», MASTER DOCUMENT).
> ⚠️ Файл `dealhunter_standards.md`, указанный в инструкции пользователя, в репозитории отсутствует — см. примечание в начале сессии.

**Дата построения индекса:** 2026-07-10
**Версия проекта:** 0.1.0 (pyproject.toml)
**Ревизия схемы БД:** `354c8b78c4f3` (initial schema, единственная миграция)

---

## 1. Общие сведения

| | |
|---|---|
| **Название** | DealHunter AI |
| **Версия** | 0.1.0 |
| **Назначение** | Интеллектуальная платформа анализа вторичного рынка объявлений: поиск выгодных предложений, аналитика (Deal Score / Risk Score / Liquidity Score — задекларировано в Конституции, ещё не реализовано), Telegram-бот как основной интерфейс |
| **Лицензия** | Proprietary (заготовка, см. `LICENSE`) |
| **Язык** | Python 3.13 |
| **Архитектурный стиль** | Модульный монолит, Clean Architecture + DDD, слои: `presentation → application → domain`, `infrastructure` реализует интерфейсы `domain`, но не наоборот |

### Технологический стек

| Слой | Технология |
|---|---|
| API | FastAPI 0.115 + Uvicorn |
| Telegram | aiogram 3.13 |
| БД | PostgreSQL 17, SQLAlchemy 2.0 (async, asyncpg) |
| Миграции | Alembic (async env) |
| Кэш/очереди/FSM | Redis 5.1 |
| Парсинг HTML | selectolax |
| Контейнеризация | Docker, Docker Compose (3 отдельных образа: api / bot / worker) |
| Тесты | pytest, pytest-asyncio, pytest-cov, httpx |
| Стиль/типизация | Black, Ruff (строгий набор правил), MyPy strict |
| Зависимости | Poetry |

---

## 2. Полное дерево проекта

```
dealhunter-ai/
├── apps/                              # Точки входа процессов (каждый — свой Docker-контейнер)
│   ├── api/main.py                    # Entrypoint FastAPI (uvicorn)
│   ├── bot/main.py                    # Entrypoint Telegram-бота (aiogram polling)
│   └── worker/main.py                 # Entrypoint фонового воркера (заготовка, без бизнес-логики)
│
├── src/dealhunter/
│   ├── core/                          # Сквозные утилиты, не относящиеся к DDD-доменам
│   │   ├── config.py                  # Settings (pydantic-settings), get_settings() — singleton
│   │   ├── logging.py                 # configure_logging(), get_logger() — единый формат логов
│   │   └── exceptions.py              # Иерархия DealHunterError → NotFound/Validation/Conflict/PermissionDenied
│   │
│   ├── domain/                        # Чистое бизнес-ядро. БЕЗ импортов FastAPI/SQLAlchemy/aiogram
│   │   ├── users/
│   │   │   ├── entities.py            # User (dataclass), UserRole, SubscriptionTier
│   │   │   └── repository.py          # UserRepository (ABC)
│   │   ├── listings/
│   │   │   └── entities.py            # Listing (dataclass), ListingStatus
│   │   │       (repository.py тоже существует — см. п.4)
│   │   ├── search/
│   │   │   ├── entities.py            # SearchProfile, SearchFilters, SearchMode, Condition, SellerType
│   │   │   └── repository.py          # SearchProfileRepository (ABC)
│   │   └── sources/
│   │       └── connector.py           # ListingFetcher (Protocol), SourceConnector (ABC)
│   │
│   ├── application/                   # Use cases — оркестрация domain через абстракции репозиториев
│   │   ├── users/use_cases.py         # RegisterUserUseCase, GetUserProfileUseCase
│   │   └── search/use_cases.py        # CreateSearchProfileUseCase, ListUserSearchesUseCase, DeleteSearchProfileUseCase
│   │
│   ├── infrastructure/                # Реализации абстракций domain
│   │   ├── db/
│   │   │   ├── base.py                # Base(DeclarativeBase) + NAMING_CONVENTION (Alembic)
│   │   │   ├── session.py             # get_engine(), get_session_factory(), get_db_session() (FastAPI dep)
│   │   │   └── models/
│   │   │       ├── __init__.py        # Реестр моделей для Alembic autogenerate
│   │   │       ├── user.py            # UserModel (табл. users)
│   │   │       ├── listing.py         # ListingModel (табл. listings)
│   │   │       └── search_profile.py  # SearchProfileModel (табл. search_profiles, filters=JSONB)
│   │   ├── repositories/
│   │   │   ├── user_repository.py     # SQLAlchemyUserRepository
│   │   │   ├── listing_repository.py  # SQLAlchemyListingRepository
│   │   │   └── search_repository.py   # SQLAlchemySearchProfileRepository (+ _filters_to/from_dict)
│   │   ├── cache/
│   │   │   └── redis_client.py        # get_redis_client() — singleton
│   │   └── sources/avito/
│   │       ├── connector.py           # AvitoConnector(SourceConnector)
│   │       ├── parser.py              # AvitoHTMLParser — чистый разбор HTML → Listing
│   │       └── fixture_fetcher.py     # FixtureListingFetcher(ListingFetcher) — тестовая/локальная реализация
│   │
│   └── presentation/                  # Тонкие адаптеры
│       ├── api/
│       │   ├── app.py                 # create_app(): FastAPI factory, lifespan, error handler mapping
│       │   ├── dependencies.py        # DI-провайдеры use case'ов для FastAPI
│       │   └── v1/routers/health.py   # GET /api/v1/health
│       └── bot/
│           ├── app.py                 # create_bot(), create_dispatcher() (RedisStorage FSM)
│           └── routers/start.py       # /start — минимальный обработчик-заглушка
│
├── migrations/
│   ├── env.py                         # Асинхронный Alembic env, DSN берётся из Settings
│   ├── script.py.mako                 # Шаблон новых миграций
│   └── versions/354c8b78c4f3_initial_schema.py   # Единственная миграция: users, listings, search_profiles
│
├── tests/
│   ├── conftest.py                    # ENV-переменные для тестов, автосброс lru_cache настроек
│   ├── unit/
│   │   ├── test_register_user_use_case.py  # RegisterUserUseCase на FakeUserRepository
│   │   ├── test_avito_parser.py            # AvitoHTMLParser, AvitoConnector, FixtureListingFetcher
│   │   └── test_health.py                  # /api/v1/health
│   └── integration/                   # Пусто — заготовка под тесты с реальной БД
│
├── docker/
│   ├── api.Dockerfile / bot.Dockerfile / worker.Dockerfile   # Однотипные образы на python:3.13-slim + poetry
├── docker-compose.yml                 # db (pg17), redis, api, bot, worker
├── alembic.ini                        # sqlalchemy.url НЕ хардкодится — подставляется из Settings
├── pyproject.toml                     # Poetry + Black/Ruff/MyPy/Pytest конфигурация
├── Makefile                           # install/run-*/migrate/test/lint/format/typecheck/check/docker-*
├── ARCHITECTURE_PRINCIPLES.md         # ★ Конституция проекта (20 статей)
├── PROJECT_CONTEXT.md                 # Мета-инструкция для AI-архитектора (этот документ реализует её Фазу 2)
├── README.md                          # Общее описание, quick start
├── LICENSE, .env.example, .gitignore, .dockerignore, .claudeignore
```

---

## 3. Архитектурная карта

### 3.1 Слои и направление зависимостей

```
presentation  →  application  →  domain
                                     ↑
infrastructure ──────────────────────┘
      (реализует интерфейсы domain; domain о ней не знает)
```

- **domain** — не импортирует ничего из FastAPI/SQLAlchemy/aiogram. Подтверждено по факту: `domain/users/entities.py`, `domain/listings/entities.py`, `domain/search/entities.py`, `domain/sources/connector.py` используют только `dataclasses`, `enum`, `abc`, `typing`.
- **application** зависит только от `domain.*.repository` (абстракции) — не от `infrastructure`. DI выполняется извне (presentation/dependencies.py).
- **infrastructure** — единственный слой, знающий про SQLAlchemy/Redis/HTTP-парсинг. Реализует `UserRepository`, `ListingRepository`, `SearchProfileRepository`, `SourceConnector`.
- **presentation** — единственный слой, знающий, откуда браться конкретным реализациям (`dependencies.py` — единственное место, где `infrastructure` встречается в presentation).

### 3.2 Три независимых процесса (Статья VI — независимость компонентов)

| Процесс | Entry point | Docker-образ | Общие ресурсы |
|---|---|---|---|
| API | `apps/api/main.py` | `docker/api.Dockerfile` | PostgreSQL, Redis |
| Bot | `apps/bot/main.py` | `docker/bot.Dockerfile` | PostgreSQL (не подключено напрямую — пока не используется), Redis (FSM) |
| Worker | `apps/worker/main.py` | `docker/worker.Dockerfile` | Пока не подключён ни к чему — `while True: sleep(60)` |

### 3.3 Ограничения, которые действуют в кодовой базе де-факто

- **Naming convention Alembic** зафиксирована в `db/base.py` — все FK/PK/UQ/CK/IX-имена детерминированы (Статья IX).
- **Деньги — только `int`, минимальные единицы валюты** (копейки). Прослеживается во всех слоях: `SearchFilters.price_min/max`, `Listing.price_minor_units`, `ListingModel.price_minor_units`.
- **UUID как PK везде**, даты — `DateTime(timezone=True)` с `server_default=func.now()`.
- **Мягкое удаление**: `deleted_at` есть в `UserModel`, `ListingModel`, `SearchProfileModel`, но ни один репозиторий пока не фильтрует по нему и не проставляет его (см. раздел 7, технический долг).
- **DSN не хардкодится** — `Settings` (pydantic-settings) единый источник и для приложения, и для Alembic (`migrations/env.py` явно подставляет `get_settings().database_url`).
- **SourceConnector изолирует парсинг от способа получения HTML** через `ListingFetcher` (Protocol) — реализовано ровно так в Avito-коннекторе.

---

## 4. Все сущности

### Entity (доменные, dataclass frozen/slots)
| Сущность | Файл | Поля/особенности |
|---|---|---|
| `User` | `domain/users/entities.py` | `role`, `subscription_tier`, `display_name`/`is_pro_or_higher` — вычисляемые свойства |
| `Listing` | `domain/listings/entities.py` | `price_minor_units`, `price_display` (property) |
| `SearchProfile` | `domain/search/entities.py` | `filters: SearchFilters`, `requires_profit_criteria()` |

### Value Object
| VO | Файл |
|---|---|
| `SearchFilters` | `domain/search/entities.py` (frozen dataclass, вложен в SearchProfile) |

### Enum
| Enum | Файл | Значения |
|---|---|---|
| `UserRole` | `domain/users/entities.py` | user / moderator / admin |
| `SubscriptionTier` | `domain/users/entities.py` | free / pro / business |
| `ListingStatus` | `domain/listings/entities.py` | active / removed / unknown |
| `SearchMode` | `domain/search/entities.py` | hunter / sniper / reseller |
| `Condition` | `domain/search/entities.py` | any / new / used |
| `SellerType` | `domain/search/entities.py` | any / private / company |

### Repository (Protocol/ABC — контракты)
| Интерфейс | Файл | Реализация |
|---|---|---|
| `UserRepository` | `domain/users/repository.py` | `SQLAlchemyUserRepository` |
| `ListingRepository` | `domain/listings/repository.py` | `SQLAlchemyListingRepository` |
| `SearchProfileRepository` | `domain/search/repository.py` | `SQLAlchemySearchProfileRepository` |

### Interface / Protocol
| | Файл |
|---|---|
| `ListingFetcher` (Protocol) | `domain/sources/connector.py` |
| `SourceConnector` (ABC) | `domain/sources/connector.py` — реализация: `AvitoConnector` |

### UseCase
| UseCase | Файл |
|---|---|
| `RegisterUserUseCase` | `application/users/use_cases.py` |
| `GetUserProfileUseCase` | `application/users/use_cases.py` |
| `CreateSearchProfileUseCase` | `application/search/use_cases.py` |
| `ListUserSearchesUseCase` | `application/search/use_cases.py` |
| `DeleteSearchProfileUseCase` | `application/search/use_cases.py` |

### ORM-модели (infrastructure)
| Модель | Таблица | Файл |
|---|---|---|
| `UserModel` | `users` | `infrastructure/db/models/user.py` |
| `ListingModel` | `listings` | `infrastructure/db/models/listing.py` |
| `SearchProfileModel` | `search_profiles` | `infrastructure/db/models/search_profile.py` |

### Schema (Pydantic)
| | Файл |
|---|---|
| `HealthResponse` | `presentation/api/v1/routers/health.py` |
| `Settings` | `core/config.py` |

*(Больше Pydantic-схем в проекте пока нет — REST-эндпоинты для users/search ещё не реализованы, только health.)*

---

## 5. Связи (кто использует кого)

```
apps/api/main.py           → presentation.api.app.create_app
apps/bot/main.py           → presentation.bot.app.{create_bot, create_dispatcher}
apps/worker/main.py        → core.config, core.logging   (бизнес-логика отсутствует)

presentation.api.app       → core.config, core.exceptions, core.logging,
                              infrastructure.db.session.get_engine,
                              presentation.api.v1.routers.health
presentation.api.dependencies → application.search.use_cases.*,
                              application.users.use_cases.*,
                              infrastructure.db.session.get_db_session,
                              infrastructure.repositories.{search_repository, user_repository}

presentation.bot.app       → core.config, presentation.bot.routers.start
presentation.bot.routers.start → (aiogram only, use case'ы бота ещё не подключены)

application.users.use_cases   → core.exceptions, domain.users.{entities, repository}
application.search.use_cases  → core.exceptions, domain.search.{entities, repository}

infrastructure.repositories.user_repository    → domain.users.{entities, repository},
                                                   infrastructure.db.models.user
infrastructure.repositories.listing_repository → domain.listings.{entities, repository},
                                                   infrastructure.db.models.listing
infrastructure.repositories.search_repository  → domain.search.{entities, repository},
                                                   infrastructure.db.models.search_profile

infrastructure.sources.avito.connector → domain.sources.connector (ListingFetcher, SourceConnector),
                                          infrastructure.sources.avito.parser
infrastructure.sources.avito.parser    → domain.listings.entities (Listing, ListingStatus)
infrastructure.sources.avito.fixture_fetcher → (реализует ListingFetcher структурно, без явного наследования — duck typing через Protocol)

infrastructure.db.models.*  → infrastructure.db.base.Base, domain.*.entities (только Enum'ы)
migrations.env              → infrastructure.db.models (__init__ — регистрация),
                               infrastructure.db.base.Base, core.config
```

### Реализуемые интерфейсы

| Интерфейс | Кто реализует |
|---|---|
| `UserRepository` | `SQLAlchemyUserRepository` |
| `ListingRepository` | `SQLAlchemyListingRepository` |
| `SearchProfileRepository` | `SQLAlchemySearchProfileRepository` |
| `SourceConnector` | `AvitoConnector` |
| `ListingFetcher` (Protocol, структурная типизация) | `FixtureListingFetcher`, `_StaticFetcher` (тестовый), (реальный сетевой fetcher для Avito — ещё не реализован) |

---

## 6. Статус реализации

| Модуль / возможность | Статус | Комментарий |
|---|---|---|
| Users: domain + repository + use cases | ✔ | Полный вертикальный срез |
| Users: REST API (создание/чтение через HTTP) | ✔ | `POST /api/v1/users/register`, `GET /api/v1/users/{id}` — роутер `presentation/api/v1/routers/users.py` |
| Users: интеграция с ботом (`/start` → `RegisterUserUseCase`) | ✔ | `start.py` вызывает use case через `SQLAlchemyUserRepository` + `get_session_factory()` |
| Search profiles: domain + repository + use cases | ✔ | Полный вертикальный срез |
| Search profiles: REST API | ✔ | `POST/GET/DELETE /api/v1/search-profiles*` — роутер `presentation/api/v1/routers/search.py` |
| Listings: domain + repository | ✔ | Entity, repository, ORM, SQLAlchemy-реализация — есть |
| Listings: use cases / API | ✖ | Application-слоя для listings нет вообще |
| Avito-коннектор: поиск (`search`) | ✔ | Парсер + коннектор + тесты |
| Avito-коннектор: получение конкретного объявления (`fetch_listing`) | ◐ | Явно `raise NotImplementedError` (осознанно, задокументировано) |
| Avito: реальный сетевой fetcher (прод) | ✖ | Есть только `FixtureListingFetcher` (файл на диске) — решение о легальном способе получения данных сознательно отложено (Статья VII) |
| Health-check (liveness) | ✔ | `/api/v1/health` |
| Health-check (readiness, БД/Redis) | ✖ | Явно отложено в docstring |
| Alembic-миграции | ✔ | Одна миграция `354c8b78c4f3` — покрывает все 3 текущие таблицы |
| Docker Compose (полный стек) | ✔ | db, redis, api, bot, worker |
| Search Scheduler / обработка очередей (Worker) | ✖ | Заготовка, `TODO` в коде |
| Deal Score / Risk Score / Liquidity Score (AI-аналитика) | ✖ | Заявлено в Конституции (Статья XVII) и в `SearchFilters` (min_deal_score, max_risk и т.п.), но алгоритмов ещё нет |
| Мягкое удаление (soft delete) на уровне репозиториев | ✖ | Поле `deleted_at` есть в моделях, но ни один репозиторий не использует его в запросах |
| Аутентификация / авторизация API | ✖ | Эндпоинтов, требующих auth, пока нет |
| Тесты: unit | ✔ | users use case, avito parser/connector, health |
| Тесты: integration | ✖ | Директория пустая, фикстур для реальной БД пока нет (осознанно, см. `tests/conftest.py`) |

---

## 7. Технический долг

- **TODO в коде**: `apps/worker/main.py` — «подключить Search Scheduler и обработку очередей Source Connectors после реализации соответствующих модулей».
- **`AvitoConnector.fetch_listing`** — намеренная заглушка (`NotImplementedError`), ждёт парсера под разметку страницы отдельного объявления.
- **Реальный `ListingFetcher` для прода** не реализован — есть только fixture-версия. Это официально описано как отдельное юридическое/архитектурное решение (Статья VII), а не забытая задача.
- ~~`deleted_at` объявлено в трёх ORM-моделях, но нигде не используется~~ — **закрыто** (2026-07-11): все три репозитория (`user_repository.py`, `listing_repository.py`, `search_repository.py`) теперь единообразно фильтруют `deleted_at IS NULL` в читающих методах.
- ~~`SearchProfileRepository.delete` делает физическое удаление~~ — **закрыто**: теперь honest soft-delete (`deleted_at = now()` вместо `session.delete()`).
- ~~`poetry.lock` не закоммичен~~ — **закрыто**: закоммичен вместе с патчем 2026-07-11.
- ~~Users REST API отсутствует~~ — **закрыто**: `POST /api/v1/users/register`, `GET /api/v1/users/{id}`.
- ~~Search profiles REST API отсутствует~~ — **закрыто**: `POST/GET/DELETE /api/v1/search-profiles*`. Замечание: `user_id` в `DELETE` передаётся query-параметром — временное решение до появления аутентификации.
- ~~Bot ↔ Users интеграция не реализована~~ — **закрыто**: `/start` вызывает `RegisterUserUseCase` напрямую через `get_session_factory()` (не через FastAPI DI — это отдельный процесс, у него нет HTTP-слоя).
- ~~`datetime.utcnow()` в `Listing`~~ — **закрыто**: заменено на `datetime.now(UTC)`, приведено в соответствие с `User`/`SearchProfile`.
- **Readiness-check** (БД/Redis) сознательно отложен — только liveness.
- **Worker** не подключён ни к БД, ни к Redis, ни к какой-либо очереди — чистая заготовка процесса.
- **AI-аналитика (Deal/Risk/Liquidity Score)** — ядро ценностного предложения продукта (Статьи II, III, XVII Конституции) полностью отсутствует в коде на этом этапе; `SearchFilters` уже содержит поля под неё (`min_deal_score`, `max_risk`, `min_confidence`), т.е. контракт данных готов, а вычисление — нет.

---

## 8. Архитектурные решения (зафиксированные)

1. **Единая таблица `listings`** вместо пары `Product`/`Listing` из более раннего прототипа — устраняет дублирование сущности (docstring `infrastructure/db/models/listing.py`).
2. **Naming convention для Alembic задаётся один раз в `Base.metadata`** — гарантирует воспроизводимые имена констрейнтов при autogenerate (Статья IX).
3. **DSN только из `Settings`**, никогда из `alembic.ini` — единственный источник конфигурации (Статья IV), явно закомментировано в `alembic.ini` и `migrations/env.py`.
4. **Деньги — `int` в минимальных единицах валюты (копейки)**, коэффициенты риска/уверенности — `float` — осознанное типовое разделение по всему домену (`SearchFilters`, `Listing`).
5. **`ListingFetcher` отделён от `SourceConnector`** — вопрос «как физически получить HTML» (юридический, Статья VII) отделён от вопроса «как это распарсить» (чисто технический). Это позволяет держать `FixtureListingFetcher` для тестов, не блокируя разработку парсера.
6. **Уникальность объявления — по паре `(source, external_id)`**, а не по одному `external_id`, так как разные площадки могут пересекаться в идентификаторах (docstring `ListingRepository.get_by_source_and_external_id`).
7. **`SearchFilters` хранится как одна колонка JSONB**, а не отдельная таблица `SearchFilters` (как в документации Тома 3) — осознанное упрощение на старте с явно задокументированным путём рефакторинга при необходимости индексов по отдельным полям.
8. **Три независимых Docker-образа** (api/bot/worker) с одним и тем же `src`/`apps` — соответствует Статье VI (независимость компонентов) при сохранении монолитной кодовой базы.
9. **Domain-слой не содержит фреймворк-зависимостей** — проверено по факту импортов: только `dataclasses`, `enum`, `abc`, `typing`, `uuid`, `datetime`.
10. **Proprietary-лицензия — явно временная заглушка** (см. комментарий в `LICENSE`), выбранная как разумный дефолт для коммерческого SaaS согласно PRD Том 10.

---

## 9. Roadmap

**Сделано:**
- Скелет Clean Architecture / DDD на двух bounded context'ах (users, search) как эталон структуры + примыкающая сущность listings.
- Полный CI-цикл локально: `make check` (lint + typecheck + test).
- Docker Compose окружение целиком (db, redis, api, bot, worker).
- Источник данных Avito: парсинг страницы поиска, конвертация в доменную модель, тесты.
- Health-check liveness.
- Async Alembic-миграции с единым источником DSN.
- REST-роутеры для users и search profiles, подключены к `create_app()`.
- Бот `/start` вызывает `RegisterUserUseCase` (идемпотентно по `telegram_id`).
- Единый soft-delete во всех трёх репозиториях.
- `poetry.lock` закоммичен — сборка образов воспроизводима.

**В работе / очевидные следующие шаги (не начаты, но контракты готовы):**
- Реальный (легальный) `ListingFetcher` для Avito в проде.
- Парсер страницы отдельного объявления Avito (`fetch_listing`).

**Дальше (по README/Конституции, не начато):**
- Остальные ~28 таблиц и сервисы из Тома 3 (DDD) / Тома 2 (SAD).
- Search Scheduler и обработка очередей в Worker.
- AI-аналитика: Deal Score / Risk Score / Liquidity Score с объяснимостью (Статьи II, III, XVII).
- Readiness-check с реальной проверкой БД/Redis.
- Soft-delete — либо реализовать фильтрацию по `deleted_at` во всех репозиториях, либо убрать поле как неиспользуемое.
- Аутентификация/авторизация API.

---

## 10. История изменений

| Дата | Изменения | Затронутые файлы | Решения |
|---|---|---|---|
| 2026-07-10 | Первичное построение PROJECT_INDEX по снимку репозитория (Фаза 1 → Фаза 2 согласно `PROJECT_CONTEXT.md`) | Весь репозиторий (85 файлов/документов на входе) | Источником Конституции считается `ARCHITECTURE_PRINCIPLES.md`; зафиксировано расхождение с упомянутым, но отсутствующим `dealhunter_standards.md`; выявлено расхождение soft-delete vs `SearchProfileRepository.delete()` (см. раздел 7, п.4) |
| 2026-07-11 | REST API для users и search-profiles; интеграция бота с `RegisterUserUseCase`; единый soft-delete во всех трёх репозиториях; фикс `datetime.utcnow()` → `datetime.now(UTC)` в `Listing`; закоммичен `poetry.lock` (первый `poetry install` в проекте) | Новые: `presentation/api/v1/routers/{users,search}.py`, `presentation/api/v1/schemas/{user,search}.py`, `tests/unit/test_users_api.py`, `poetry.lock`. Изменены: `presentation/api/app.py`, `presentation/bot/routers/start.py`, `infrastructure/repositories/{user,listing,search}_repository.py`, `domain/listings/entities.py` | 1) Интерфейсы `*Repository` не менялись (не добавлялись новые abstract-методы) — чтобы не сломать `FakeUserRepository` в существующих тестах. 2) `DELETE /search-profiles/{id}` пока принимает `user_id` в query — временное решение до аутентификации, явно задокументировано в коде. 3) `response_model=None` обязателен на FastAPI-эндпоинтах со статусом 204 — иначе FastAPI выводит `NoneType` из аннотации возврата и падает на `is_body_allowed_for_status_code`. Проверено локально: `ruff` — 0 замечаний, `mypy --strict` — 0 ошибок (57 файлов), `pytest` — 16/16 passed |

---

## Как пользоваться этим индексом дальше

При следующей синхронизации (`git push` → Refresh в Data Sources → новое сообщение в чат):
1. Дайте команду вида «сравни с PROJECT_INDEX и обнови» — я не буду анализировать проект с нуля (Фаза 3 из `PROJECT_CONTEXT.md`), а сравню снимок и обновлю только изменившиеся разделы.
2. Перед любой новой задачей я сверяюсь с разделами 3 (архитектурная карта), 6 (статус) и 7 (технический долг) этого индекса, чтобы предлагать минимальные, архитектурно согласованные изменения.
