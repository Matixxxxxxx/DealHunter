"""Коннектор источника Avito — реализация контракта из Тома 8.

Намеренно не содержит логику получения "сырых" данных из сети — она
инжектируется через `ListingFetcher` (Dependency Injection). Это отделяет
архитектурный вопрос ("как устроен коннектор") от бизнес/юридического
вопроса ("каким легальным способом получать данные Avito") — второй
требует отдельного осознанного решения, см. `dealhunter.domain.sources.
connector.ListingFetcher`.
"""

from __future__ import annotations

from dealhunter.domain.listings.entities import Listing
from dealhunter.domain.sources.connector import ListingFetcher, SourceConnector
from dealhunter.infrastructure.sources.avito.parser import AvitoHTMLParser


class AvitoConnector(SourceConnector):
    """Коннектор Avito, реализующий единый контракт `SourceConnector`."""

    source_name = "avito"

    def __init__(self, fetcher: ListingFetcher, parser: AvitoHTMLParser | None = None) -> None:
        self._fetcher = fetcher
        self._parser = parser or AvitoHTMLParser()

    async def initialize(self) -> None:
        """Ресурсов, требующих явной инициализации, пока нет."""

    async def search(self, query: str) -> list[Listing]:
        html = await self._fetcher.fetch_search_html(query)
        return self._parser.parse_search_results(html)

    async def fetch_listing(self, external_id: str) -> Listing | None:
        html = await self._fetcher.fetch_listing_html(external_id)
        if html is None:
            return None
        # Страница отдельного объявления имеет другую разметку, чем страница
        # поиска — отдельный парсер для неё добавляется вместе с реальным
        # fetcher'ом, когда будет принято решение по способу получения данных.
        raise NotImplementedError(
            "Разбор страницы отдельного объявления пока не реализован — "
            "требуется парсер под разметку страницы объявления Avito"
        )

    async def health_check(self) -> bool:
        return True

    async def shutdown(self) -> None:
        """Ресурсов, требующих явного освобождения, пока нет."""
