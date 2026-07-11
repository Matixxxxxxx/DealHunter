"""REST-эндпоинты пользователей.

Тонкий адаптер: весь бизнес-смысл — в use case'ах, роутер только
конвертирует HTTP ⇄ DTO и вызывает use case (Статья VI Конституции).
"""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from dealhunter.application.users.use_cases import GetUserProfileUseCase, RegisterUserUseCase
from dealhunter.presentation.api.dependencies import (
    get_register_user_use_case,
    get_user_profile_use_case,
)
from dealhunter.presentation.api.v1.schemas.user import RegisterUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: RegisterUserRequest,
    use_case: Annotated[RegisterUserUseCase, Depends(get_register_user_use_case)],
) -> UserResponse:
    """Регистрирует пользователя (идемпотентно по telegram_id).

    Тот же use case вызывается ботом при `/start` — REST-путь пригодится
    для внешних интеграций и локального тестирования без Telegram.
    """
    user = await use_case.execute(
        telegram_id=payload.telegram_id,
        username=payload.username,
        first_name=payload.first_name,
        last_name=payload.last_name,
        language=payload.language,
    )
    return UserResponse.from_entity(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: UUID,
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
) -> UserResponse:
    """Возвращает профиль пользователя. 404 — через `NotFoundError` (см. app.py)."""
    user = await use_case.execute(user_id)
    return UserResponse.from_entity(user)
