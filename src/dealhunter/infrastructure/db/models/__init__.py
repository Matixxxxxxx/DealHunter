"""Импортирует все ORM-модели, чтобы они регистрировались в Base.metadata.

Alembic (migrations/env.py) импортирует именно этот модуль — благодаря
этому autogenerate видит все таблицы проекта. При добавлении новой модели
её обязательно нужно импортировать здесь.
"""

from dealhunter.infrastructure.db.models.listing import ListingModel
from dealhunter.infrastructure.db.models.search_profile import SearchProfileModel
from dealhunter.infrastructure.db.models.user import UserModel

__all__ = ["UserModel", "SearchProfileModel", "ListingModel"]
