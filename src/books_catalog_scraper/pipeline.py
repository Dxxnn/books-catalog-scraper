"""End-to-end catalogue extraction pipeline."""

from __future__ import annotations

import logging
from urllib.parse import urlparse

from .config import ScraperConfig
from .exporter import export_results, records_to_frame
from .http_client import PoliteRequester, build_session
from .models import BookRecord
from .parser import parse_catalogue_page
from .robots import RobotsPolicyError, load_robots_policy


class CrawlSafetyError(RuntimeError):
    """Raised when a URL violates the configured crawl boundary."""


def _same_origin(base_url: str, target_url: str) -> bool:
    base = urlparse(base_url)
    target = urlparse(target_url)
    return (
        base.scheme.lower(),
        base.hostname,
        base.port,
    ) == (
        target.scheme.lower(),
        target.hostname,
        target.port,
    )


def run_pipeline(
    config: ScraperConfig,
    logger: logging.Logger,
) -> dict[str, object]:
    config.validate()
    session = build_session(config.user_agent)
    try:
        policy = load_robots_policy(
            config.base_url,
            session,
            config.user_agent,
            config.timeout_seconds,
        )
        logger.info(
            "Política robots: %s (%s)",
            policy.status,
            policy.robots_url,
        )

        requester = PoliteRequester(
            session=session,
            delay_seconds=config.delay_seconds,
            timeout_seconds=config.timeout_seconds,
            logger=logger,
        )
        if policy.crawl_delay_seconds is not None:
            requester.set_minimum_delay(policy.crawl_delay_seconds)
            logger.info(
                "Crawl-delay efectivo: %.2f segundos.",
                requester.delay_seconds,
            )

        records: list[BookRecord] = []
        current_url: str | None = config.base_url

        for page_number in range(1, config.max_pages + 1):
            if current_url is None:
                logger.info("No hay una página siguiente; recorrido finalizado.")
                break
            if not _same_origin(config.base_url, current_url):
                raise CrawlSafetyError(
                    f"Se rechazó una URL fuera del origen autorizado: {current_url}"
                )
            if not policy.allows(current_url):
                raise RobotsPolicyError(
                    f"robots.txt no permite solicitar: {current_url}"
                )

            response = requester.get(current_url)
            page_records, next_url = parse_catalogue_page(
                response.text,
                current_url,
                page_number,
            )
            records.extend(page_records)
            logger.info(
                "Página %d: %d registros extraídos.",
                page_number,
                len(page_records),
            )
            current_url = next_url

        frame = records_to_frame(records)
        paths = export_results(frame, config.output_dir)
        logger.info(
            "Finalizado: %d registros únicos en %s.",
            len(frame),
            config.output_dir,
        )
        return {
            "record_count": int(len(frame)),
            "paths": paths,
            "robots_status": policy.status,
            "effective_delay_seconds": requester.delay_seconds,
        }
    finally:
        session.close()
