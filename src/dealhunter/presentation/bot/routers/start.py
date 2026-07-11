"""Обработчик команды /start.

Теперь `/start` действительно регистрирует пользователя через
`RegisterUserUseCase` (идемпотентно по `telegram_id`) — раньше use case
существовал, но не был подключён к боту, хотя явно написан под этот
сценарий (см. docstring `RegisterUserUseCase`).

Полная бизнес-логика бота (главное меню, мастер создания поиска и т.д. —
Том 6 Telegram Bot Design) переносится сюда отдельными задачами из
существующего прототипа.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from dealhunter.application.users.use_cases import RegisterUserUseCase
from dealhunter.core.logging import get_logger
from dealhunter.infrastructure.db.session import get_session_factory
from dealhunter.infrastructure.repositories.user_repository import SQLAlchemyUserRepository

router = Router(name="start")
logger = get_logger(__name__)


@router.message(CommandStart())
async def cmd_start(message: Message) -> None:
    if message.from_user is not None and not message.from_user.is_bot:
        session_factory = get_session_factory()
        async with session_factory() as session:
            use_case = RegisterUserUseCase(user_repository=SQLAlchemyUserRepository(session))
            await use_case.execute(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language=message.from_user.language_code or "ru",
            )
    else:
        logger.warning("/start получен без данных отправителя — пользователь не зарегистрирован")

    await message.answer(
        "👋 DealHunter AI запущен.\n\n"
        "Это техническая версия бота на новой промышленной архитектуре. "
        "Полный функционал (поиски, аналитика, PRO) переносится сюда "
        "поэтапно."
    )
