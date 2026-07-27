"""HTTP session with moderate retries and rate limiting."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def build_session(user_agent: str) -> requests.Session:
    retry = Retry(
        total=3,
        connect=3,
        read=3,
        status=3,
        backoff_factor=0.8,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET", "HEAD"}),
        respect_retry_after_header=True,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "es,en;q=0.8",
        }
    )
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


@dataclass
class PoliteRequester:
    session: requests.Session
    delay_seconds: float
    timeout_seconds: float
    logger: logging.Logger
    _last_request_at: float | None = field(default=None, init=False)

    def set_minimum_delay(self, delay_seconds: float) -> None:
        self.delay_seconds = max(self.delay_seconds, delay_seconds)

    def get(self, url: str) -> requests.Response:
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            wait_for = self.delay_seconds - elapsed
            if wait_for > 0:
                self.logger.debug("Pausa responsable de %.2f segundos.", wait_for)
                time.sleep(wait_for)

        self.logger.info("GET %s", url)
        try:
            response = self.session.get(url, timeout=self.timeout_seconds)
            self._last_request_at = time.monotonic()
            response.raise_for_status()
            return response
        except requests.RequestException:
            self._last_request_at = time.monotonic()
            self.logger.exception("Falló la solicitud a %s", url)
            raise
