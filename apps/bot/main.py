"""Entrypoint процесса Telegram-бота. Запуск: `python -m apps.bot.main`."""

from __future__ import annotations

import asyncio

from dealhunter.core.config import get_settings
from dealhunter.core.logging import configure_logging, get_logger
from dealhunter.presentation.bot.app import create_bot, create_dispatcher

logger = get_logger(__name__)


async def main() -> None:
    settings = get_settings()
    configure_logging(settings.log_level)
    logger.info("DealHunter Bot стартует (environment=%s)", settings.environment)

    bot = create_bot()
    dispatcher = create_dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await dispatcher.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
