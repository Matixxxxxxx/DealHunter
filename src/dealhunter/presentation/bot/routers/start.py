"""Обработчик команды /start.

Полная бизнес-логика бота (главное меню, мастер создания поиска и т.д. —
Том 6 Telegram Bot Design) переносится сюда отдельной задачей из
существующего прототипа. Сейчас — минимальный обработчик, подтверждающий,
что presentation/bot корректно подключается к приложению.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    await message.answer(
        "👋 DealHunter AI запущен.\n\n"
        "Это техническая версия бота на новой промышленной архитектуре. "
        "Полный функционал (поиски, аналитика, PRO) переносится сюда "
        "поэтапно."
    )
