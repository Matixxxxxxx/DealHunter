"""Фабрика Bot/Dispatcher для Telegram-клиента (Том 2 SAD, раздел 9)."""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from dealhunter.core.config import get_settings
from dealhunter.presentation.bot.routers import start


def create_bot() -> Bot:
    """Создаёт экземпляр Bot с настройками по умолчанию (HTML-разметка)."""
    settings = get_settings()
    return Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def create_dispatcher() -> Dispatcher:
    """Создаёт Dispatcher с FSM-хранилищем в Redis и подключёнными роутерами.

    Redis как FSM storage (вместо MemoryStorage) обязателен вне local-разработки:
    он переживает перезапуск процесса и работает корректно при нескольких
    инстансах бота (Том 2 SAD, раздел 18).
    """
    settings = get_settings()
    storage = RedisStorage.from_url(settings.redis_url)
    dispatcher = Dispatcher(storage=storage)

    dispatcher.include_router(start.router)

    return dispatcher
