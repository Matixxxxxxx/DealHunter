"""Разбор HTML-страниц Avito в доменную модель `Listing`.

Селекторы (`data-marker="item"` и т.д.) — рабочая находка из более раннего
прототипа, перенесена как есть. Модуль сознательно не содержит ни одного
сетевого вызова: на вход подаётся уже полученный откуда-то HTML, на выходе —
список доменных сущностей. Как именно HTML был получен — забота
`ListingFetcher` (см. `dealhunter.domain.sources.connector`), а не этого
модуля.
"""

from __future__ import annotations

import re
from uuid import uuid4

from selectolax.parser import HTMLParser, Node

from dealhunter.domain.listings.entities import Listing, ListingStatus

_DIGITS_RE = re.compile(r"\D")


def _extract_price_minor_units(price_text: str | None) -> int | None:
    """Парсит текст вида "45 000 ₽" в минимальные единицы валюты (копейки)."""
    if not price_text:
        return None

    digits = _DIGITS_RE.sub("", price_text)
    if not digits:
        return None

    rubles = int(digits)
    return rubles * 100


class AvitoHTMLParser:
    """Извлекает список объявлений из HTML страницы результатов поиска Avito."""

    SOURCE_NAME = "avito"
    BASE_URL = "https://www.avito.ru"

    def parse_search_results(self, html: str) -> list[Listing]:
        """Разбирает HTML страницы поиска в список доменных `Listing`.

        Каждому найденному объявлению присваивается новый UUID — это
        "кандидат" сущности; окончательное решение "новое это объявление
        или обновление уже известного" принимает вызывающий код на основе
        `ListingRepository.get_by_source_and_external_id()` (Том 8,
        раздел 8 — дедупликация).
        """
        tree = HTMLParser(html)
        listings: list[Listing] = []

        for card in tree.css('[data-marker="item"]'):
            listing = self._parse_card(card)
            if listing is not None:
                listings.append(listing)

        return listings

    def _parse_card(self, card: Node) -> Listing | None:
        title_node = card.css_first('[data-marker="item-title"]')
        if title_node is None:
            return None

        title = title_node.text(strip=True)
        if not title:
            return None

        href = title_node.attributes.get("href", "") or ""
        url = self.BASE_URL + href if href.startswith("/") else href

        external_id = self._extract_external_id(href)
        if external_id is None:
            return None

        price_node = card.css_first('[data-marker="item-price"]')
        price_minor_units = _extract_price_minor_units(
            price_node.text(strip=True) if price_node else None
        )

        location_node = card.css_first('[data-marker="item-location"]')
        location = location_node.text(strip=True) if location_node else None

        image_node = card.css_first("img")
        image_url = None
        if image_node is not None:
            image_url = image_node.attributes.get("src") or image_node.attributes.get(
                "data-src"
            )

        return Listing(
            id=uuid4(),
            source=self.SOURCE_NAME,
            external_id=external_id,
            title=title,
            url=url,
            price_minor_units=price_minor_units,
            location=location,
            image_url=image_url,
            status=ListingStatus.ACTIVE,
        )

    @staticmethod
    def _extract_external_id(href: str) -> str | None:
        """Извлекает ID объявления из URL вида `/moskva/.../item_XXXXX_YYYYY`.

        Avito кодирует уникальный ID объявления как последний числовой
        сегмент, отделённый подчёркиванием, в конце пути.
        """
        if not href:
            return None
        match = re.search(r"_(\d+)(?:\?.*)?$", href)
        return match.group(1) if match else None
