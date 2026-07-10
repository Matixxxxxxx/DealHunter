"""Настройка структурированного логирования.

Согласно Статье XI Конституции («Наблюдаемость»), любой важный процесс
должен быть наблюдаемым: что произошло, когда, почему и с каким результатом.
Единый формат логов на старте проекта упрощает последующую интеграцию с
централизованным сбором логов (ELK/Loki/Datadog и т.п.).
"""

from __future__ import annotations

import logging
import sys

from dealhunter.core.config import LogLevel

_LOG_FORMAT = (
    "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
)
_DATE_FORMAT = "%Y-%m-%dT%H:%M:%S%z"


def configure_logging(log_level: LogLevel = "INFO") -> None:
    """Инициализирует корневой логгер приложения.

    Вызывается один раз при старте каждого процесса (API / Bot / Worker).
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Не дублируем хендлеры при повторном вызове (например, в тестах).
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(fmt=_LOG_FORMAT, datefmt=_DATE_FORMAT))
    root_logger.addHandler(handler)

    # Шумные библиотеки — приглушаем до WARNING, чтобы не заваливать логи.
    for noisy_logger in ("uvicorn.access", "aiogram.event"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Возвращает именованный логгер модуля."""
    return logging.getLogger(name)
