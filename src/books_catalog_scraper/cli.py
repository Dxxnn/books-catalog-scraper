"""Command-line interface."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .config import DEFAULT_USER_AGENT, ScraperConfig
from .pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Extrae de forma responsable el catálogo público de Books to Scrape."
        )
    )
    parser.add_argument(
        "--base-url",
        default="https://books.toscrape.com/",
        help="URL inicial del catálogo.",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=5,
        help="Número de páginas entre 1 y 50 (predeterminado: 5).",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=1.0,
        help="Pausa mínima entre solicitudes, en segundos (mínimo: 0.5).",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="Timeout de cada solicitud, en segundos.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("data/output"),
        help="Carpeta de resultados.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=Path("logs/scraper.log"),
        help="Archivo de log.",
    )
    parser.add_argument(
        "--user-agent",
        default=DEFAULT_USER_AGENT,
        help="User-Agent identificable.",
    )
    return parser


def configure_logging(log_file: Path) -> logging.Logger:
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("books_catalog_scraper")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


def main() -> None:
    args = build_parser().parse_args()
    config = ScraperConfig(
        base_url=args.base_url,
        max_pages=args.max_pages,
        delay_seconds=args.delay,
        timeout_seconds=args.timeout,
        output_dir=args.output_dir,
        log_file=args.log_file,
        user_agent=args.user_agent,
    )
    logger = configure_logging(config.log_file)
    try:
        result = run_pipeline(config, logger)
    except (RuntimeError, ValueError) as exc:
        logger.error("%s", exc)
        raise SystemExit(1) from exc

    print(f"Registros: {result['record_count']}")
    for label, path in result["paths"].items():
        print(f"{label}: {path}")
