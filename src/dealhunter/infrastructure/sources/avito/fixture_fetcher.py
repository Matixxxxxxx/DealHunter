"""Fixture-реализация `ListingFetcher` для тестов и локальной разработки.

Читает заранее сохранённый HTML-файл вместо обращения к сети. Не выполняет
никаких запросов к Avito — полностью безопасна с точки зрения Статьи VII
Конституции.

Реализация, которая реально получает данные в проде (официальный API,
лицензированный фид или прямой HTTP-запрос) — отдельное решение,
принимаемое осознанно, см. docstring `ListingFetcher`.
"""

from __future__ import annotations

from pathlib import Path


class FixtureListingFetcher:
    """Отдаёт содержимое локального HTML-файла как "результат поиска"."""

    def __init__(self, search_html_path: Path | str) -> None:
        self._search_html_path = Path(search_html_path)

    async def fetch_search_html(self, query: str) -> str:
        return self._search_html_path.read_text(encoding="utf-8")

    async def fetch_listing_html(self, external_id: str) -> str | None:
        # Для fixture-режима отдельные страницы объявлений не поддерживаются.
        return None
