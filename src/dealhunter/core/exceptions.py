"""Единая иерархия исключений уровня приложения.

Domain- и application-слои поднимают только эти исключения (не
SQLAlchemy/HTTP-специфичные) — presentation-слой (FastAPI) транслирует их
в HTTP-ответы. Это сохраняет независимость бизнес-логики от фреймворков
(Статья VI Конституции).
"""

from __future__ import annotations


class DealHunterError(Exception):
    """Базовое исключение для всех ошибок приложения."""


class NotFoundError(DealHunterError):
    """Запрашиваемая сущность не найдена."""


class ValidationError(DealHunterError):
    """Данные не прошли бизнес-валидацию."""


class ConflictError(DealHunterError):
    """Операция конфликтует с текущим состоянием данных (например, дубликат)."""


class PermissionDeniedError(DealHunterError):
    """У пользователя недостаточно прав для выполнения операции."""
