"""HTML parsing for Books to Scrape catalogue pages."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .models import BookRecord


RATING_MAP = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class CatalogueParseError(ValueError):
    """Raised when a page does not contain the expected catalogue structure."""


def _normalize_space(value: str) -> str:
    return " ".join(value.split())


def _parse_price(value: str) -> float:
    match = re.search(r"(\d+(?:\.\d{1,2})?)", value.replace(",", ""))
    if not match:
        raise CatalogueParseError(f"No se pudo interpretar el precio: {value!r}")
    return float(match.group(1))


def _parse_rating(class_names: list[str]) -> int:
    for name in class_names:
        if name in RATING_MAP:
            return RATING_MAP[name]
    raise CatalogueParseError(
        f"No se encontró una calificación válida en: {class_names!r}"
    )


def parse_catalogue_page(
    html: str,
    page_url: str,
    page_number: int,
    scraped_at_utc: str | None = None,
) -> tuple[list[BookRecord], str | None]:
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("article.product_pod")
    if not cards:
        raise CatalogueParseError(
            "La página no contiene tarjetas article.product_pod."
        )

    scraped_at = scraped_at_utc or datetime.now(timezone.utc).isoformat()
    records: list[BookRecord] = []

    for index, card in enumerate(cards, start=1):
        anchor = card.select_one("h3 a")
        price = card.select_one("p.price_color")
        availability = card.select_one("p.instock.availability")
        rating = card.select_one("p.star-rating")
        if not all((anchor, price, availability, rating)):
            raise CatalogueParseError(
                f"La tarjeta {index} no contiene todos los campos requeridos."
            )

        href = anchor.get("href")
        if not href:
            raise CatalogueParseError(f"La tarjeta {index} no tiene URL.")

        title = _normalize_space(anchor.get("title") or anchor.get_text(" ", strip=True))
        availability_text = _normalize_space(
            availability.get_text(" ", strip=True)
        )
        records.append(
            BookRecord(
                title=title,
                price_gbp=_parse_price(price.get_text(" ", strip=True)),
                availability=availability_text,
                in_stock="in stock" in availability_text.lower(),
                rating=_parse_rating(rating.get("class", [])),
                product_url=urljoin(page_url, href),
                source_page=page_number,
                scraped_at_utc=scraped_at,
            )
        )

    next_anchor = soup.select_one("li.next a")
    next_url = (
        urljoin(page_url, next_anchor.get("href"))
        if next_anchor and next_anchor.get("href")
        else None
    )
    return records, next_url
