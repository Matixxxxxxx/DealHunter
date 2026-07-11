"""REST-эндпоинты поисковых профилей ("Мои поиски", Том 1 PRD)."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from dealhunter.application.search.use_cases import (
    CreateSearchProfileUseCase,
    DeleteSearchProfileUseCase,
    ListUserSearchesUseCase,
)
from dealhunter.presentation.api.dependencies import (
    get_create_search_profile_use_case,
    get_delete_search_profile_use_case,
    get_list_user_searches_use_case,
)
from dealhunter.presentation.api.v1.schemas.search import (
    CreateSearchProfileRequest,
    SearchProfileResponse,
)

router = APIRouter(prefix="/search-profiles", tags=["search-profiles"])


@router.post("", response_model=SearchProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_search_profile(
    payload: CreateSearchProfileRequest,
    use_case: Annotated[CreateSearchProfileUseCase, Depends(get_create_search_profile_use_case)],
) -> SearchProfileResponse:
    profile = await use_case.execute(
        user_id=payload.user_id,
        name=payload.name,
        mode=payload.mode,
        filters=payload.filters.to_domain(),
    )
    return SearchProfileResponse.from_entity(profile)


@router.get("/user/{user_id}", response_model=list[SearchProfileResponse])
async def list_user_search_profiles(
    user_id: UUID,
    use_case: Annotated[ListUserSearchesUseCase, Depends(get_list_user_searches_use_case)],
) -> list[SearchProfileResponse]:
    profiles = await use_case.execute(user_id)
    return [SearchProfileResponse.from_entity(profile) for profile in profiles]


@router.delete("/{profile_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_search_profile(
    profile_id: UUID,
    user_id: UUID,
    use_case: Annotated[DeleteSearchProfileUseCase, Depends(get_delete_search_profile_use_case)],
) -> None:
    """`user_id` пока передаётся query-параметром.

    Это временное решение до появления аутентификации в проекте — тогда
    `user_id` будет браться из авторизованной сессии, а не из запроса
    (см. PROJECT_INDEX.md, раздел 7 «Технический долг»).
    """
    await use_case.execute(user_id=user_id, profile_id=profile_id)
