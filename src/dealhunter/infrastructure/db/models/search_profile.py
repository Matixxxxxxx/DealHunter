"""ORM-модель таблицы `search_profiles` — Том 3 DDD, разделы 8-9.

Фильтры (SearchFilters) хранятся в JSONB одной колонкой — в документации
(Том 3, раздел 9) они выделены в отдельную таблицу `SearchFilters`, но на
старте проекта JSONB достаточен и позволяет добавлять новые поля фильтров
без миграций схемы. Вынесение в отдельную таблицу — тривиальный будущий
рефакторинг при необходимости построения индексов по конкретным полям
фильтра.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column

from dealhunter.domain.search.entities import SearchMode
from dealhunter.infrastructure.db.base import Base


class SearchProfileModel(Base):
    """Таблица поисковых профилей пользователей."""

    __tablename__ = "search_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    mode: Mapped[SearchMode] = mapped_column(
        Enum(SearchMode, name="search_mode", native_enum=False), nullable=False
    )
    filters: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, default=None
    )
