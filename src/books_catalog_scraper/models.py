"""Data models used by the extraction pipeline."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BookRecord:
    title: str
    price_gbp: float
    availability: str
    in_stock: bool
    rating: int
    product_url: str
    source_page: int
    scraped_at_utc: str
