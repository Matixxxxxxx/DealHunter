"""Тесты AvitoHTMLParser и AvitoConnector.

HTML-фикстура ниже написана вручную и воспроизводит только структуру
разметки (атрибуты `data-marker`), которую использует парсер — не является
скопированной страницей Avito.
"""

from __future__ import annotations

import pytest

from dealhunter.domain.listings.entities import ListingStatus
from dealhunter.infrastructure.sources.avito.connector import AvitoConnector
from dealhunter.infrastructure.sources.avito.parser import AvitoHTMLParser

_SAMPLE_SEARCH_HTML = """
<html><body>
<div data-marker="item">
    <a data-marker="item-title" href="/moskva/videokarty/rtx_4070_asus_dual_1234567890">
        RTX 4070 ASUS Dual
    </a>
    <span data-marker="item-price">41 000 ₽</span>
    <span data-marker="item-location">Москва</span>
    <img data-src="https://example.com/rtx4070.jpg" />
</div>
<div data-marker="item">
    <a data-marker="item-title" href="/spb/videokarty/rtx_4060_1234567891">
        RTX 4060
    </a>
    <span data-marker="item-price">28 500 ₽</span>
    <span data-marker="item-location">Санкт-Петербург</span>
</div>
<div data-marker="item">
    <!-- Объявление без заголовка — должно быть пропущено парсером -->
    <span data-marker="item-price">10 000 ₽</span>
</div>
</body></html>
"""


class TestAvitoHTMLParser:
    def test_parses_all_valid_cards(self) -> None:
        parser = AvitoHTMLParser()

        listings = parser.parse_search_results(_SAMPLE_SEARCH_HTML)

        assert len(listings) == 2

    def test_extracts_fields_correctly(self) -> None:
        parser = AvitoHTMLParser()

        listings = parser.parse_search_results(_SAMPLE_SEARCH_HTML)
        first = listings[0]

        assert first.title == "RTX 4070 ASUS Dual"
        assert first.external_id == "1234567890"
        assert first.url == "https://www.avito.ru/moskva/videokarty/rtx_4070_asus_dual_1234567890"
        assert first.price_minor_units == 41_000 * 100
        assert first.location == "Москва"
        assert first.image_url == "https://example.com/rtx4070.jpg"
        assert first.status == ListingStatus.ACTIVE
        assert first.source == "avito"

    def test_handles_missing_price_gracefully(self) -> None:
        parser = AvitoHTMLParser()
        html_without_price = """
        <div data-marker="item">
            <a data-marker="item-title" href="/item_9999">No price item</a>
        </div>
        """

        listings = parser.parse_search_results(html_without_price)

        assert listings[0].price_minor_units is None

    def test_skips_cards_without_title(self) -> None:
        parser = AvitoHTMLParser()

        listings = parser.parse_search_results(_SAMPLE_SEARCH_HTML)

        # Третья карточка без заголовка не должна попасть в результат.
        assert all(listing.title for listing in listings)


class _StaticFetcher:
    """Простейшая in-memory реализация ListingFetcher для теста коннектора."""

    def __init__(self, html: str) -> None:
        self._html = html

    async def fetch_search_html(self, query: str) -> str:
        return self._html

    async def fetch_listing_html(self, external_id: str) -> str | None:
        return None


class TestAvitoConnector:
    @pytest.mark.asyncio
    async def test_search_returns_parsed_listings(self) -> None:
        connector = AvitoConnector(fetcher=_StaticFetcher(_SAMPLE_SEARCH_HTML))

        results = await connector.search("RTX 4070")

        assert len(results) == 2
        assert results[0].source == "avito"

    @pytest.mark.asyncio
    async def test_fetch_listing_not_yet_implemented(self) -> None:
        """Явно фиксирует, что разбор страницы объявления пока не реализован —
        см. обоснование в docstring AvitoConnector.fetch_listing."""

        class _FetcherWithListingPage(_StaticFetcher):
            async def fetch_listing_html(self, external_id: str) -> str | None:
                return "<html>some listing page</html>"

        connector = AvitoConnector(fetcher=_FetcherWithListingPage(_SAMPLE_SEARCH_HTML))

        with pytest.raises(NotImplementedError):
            await connector.fetch_listing("1234567890")

    @pytest.mark.asyncio
    async def test_health_check_returns_true(self) -> None:
        connector = AvitoConnector(fetcher=_StaticFetcher(_SAMPLE_SEARCH_HTML))

        assert await connector.health_check() is True


class TestFixtureListingFetcher:
    @pytest.mark.asyncio
    async def test_reads_html_from_local_file(self, tmp_path: object) -> None:
        from dealhunter.infrastructure.sources.avito.fixture_fetcher import (
            FixtureListingFetcher,
        )

        html_file = tmp_path / "search_results.html"  # type: ignore[operator]
        html_file.write_text(_SAMPLE_SEARCH_HTML, encoding="utf-8")  # type: ignore[union-attr]

        fetcher = FixtureListingFetcher(html_file)
        html = await fetcher.fetch_search_html(query="RTX 4070")

        assert "RTX 4070 ASUS Dual" in html

    @pytest.mark.asyncio
    async def test_fetch_listing_html_returns_none(self, tmp_path: object) -> None:
        from dealhunter.infrastructure.sources.avito.fixture_fetcher import (
            FixtureListingFetcher,
        )

        html_file = tmp_path / "search_results.html"  # type: ignore[operator]
        html_file.write_text(_SAMPLE_SEARCH_HTML, encoding="utf-8")  # type: ignore[union-attr]

        fetcher = FixtureListingFetcher(html_file)

        assert await fetcher.fetch_listing_html("1234567890") is None
