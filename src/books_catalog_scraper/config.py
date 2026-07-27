"""Configuration and safety limits for the scraper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlparse


DEFAULT_USER_AGENT = (
    "DanielPortfolioScraper/1.0 "
    "(+https://github.com/Dxxnn/books-catalog-scraper)"
)


@dataclass(frozen=True)
class ScraperConfig:
    base_url: str = "https://books.toscrape.com/"
    max_pages: int = 5
    delay_seconds: float = 1.0
    timeout_seconds: float = 15.0
    output_dir: Path = Path("data/output")
    log_file: Path = Path("logs/scraper.log")
    user_agent: str = DEFAULT_USER_AGENT

    def validate(self) -> "ScraperConfig":
        parsed = urlparse(self.base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("base_url debe ser una URL HTTP(S) válida.")
        if not 1 <= self.max_pages <= 50:
            raise ValueError("max_pages debe estar entre 1 y 50.")
        if self.delay_seconds < 0.5:
            raise ValueError("delay_seconds no puede ser menor que 0,5.")
        if not 1 <= self.timeout_seconds <= 60:
            raise ValueError("timeout_seconds debe estar entre 1 y 60.")
        if not self.user_agent.strip():
            raise ValueError("user_agent no puede estar vacío.")
        return self
