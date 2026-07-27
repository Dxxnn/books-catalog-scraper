"""robots.txt retrieval and enforcement."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urljoin
from urllib.robotparser import RobotFileParser

import requests


class RobotsPolicyError(RuntimeError):
    """Raised when a robots policy cannot be checked safely."""


@dataclass(frozen=True)
class RobotsPolicy:
    parser: RobotFileParser
    user_agent: str
    robots_url: str
    status: str
    crawl_delay_seconds: float | None

    def allows(self, url: str) -> bool:
        return self.parser.can_fetch(self.user_agent, url)


def load_robots_policy(
    base_url: str,
    session: requests.Session,
    user_agent: str,
    timeout_seconds: float,
) -> RobotsPolicy:
    robots_url = urljoin(base_url, "/robots.txt")
    parser = RobotFileParser()
    parser.set_url(robots_url)

    try:
        response = session.get(robots_url, timeout=timeout_seconds)
    except requests.RequestException as exc:
        raise RobotsPolicyError(
            f"No fue posible consultar robots.txt: {exc}"
        ) from exc

    if response.status_code == 404:
        parser.allow_all = True
        return RobotsPolicy(
            parser=parser,
            user_agent=user_agent,
            robots_url=robots_url,
            status="not_found",
            crawl_delay_seconds=None,
        )

    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise RobotsPolicyError(
            f"robots.txt respondió con estado {response.status_code}; "
            "se detuvo el recorrido."
        ) from exc

    parser.parse(response.text.splitlines())
    delay = parser.crawl_delay(user_agent)
    if delay is None:
        delay = parser.crawl_delay("*")

    return RobotsPolicy(
        parser=parser,
        user_agent=user_agent,
        robots_url=robots_url,
        status="loaded",
        crawl_delay_seconds=float(delay) if delay is not None else None,
    )
