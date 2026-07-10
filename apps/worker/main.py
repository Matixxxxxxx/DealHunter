"""Entrypoint фонового воркера.

Заготовка под Search Scheduler / Source Connectors (Том 2 SAD, разделы 8, 9;
Том 5 Search Engine Design). Реальная логика планирования и обработки
очередей будет реализована отдельными задачами — сейчас процесс лишь
демонстрирует, что в архитектуре предусмотрен отдельный контейнер для
фоновой обработки, не зависящий от API и бота.
"""

from __future__ import annotations

import asyncio

from dealhunter.core.config import get_settings
from dealhunter.core.logging import configure_logging, get_logger

logger = get_logger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("DealHunter Worker стартует (environment=%s)", settings.environment)

    # TODO: подключить Search Scheduler и обработку очередей Source Connectors
    # после реализации соответствующих модулей (Том 2, Том 5, Том 8).
    logger.warning("Worker пока не содержит бизнес-логики — заготовка для будущих задач")

    while True:
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(main())
