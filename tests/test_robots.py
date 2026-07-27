import unittest

from books_catalog_scraper.robots import load_robots_policy


class DummyResponse:
    def __init__(self, status_code: int, text: str = "") -> None:
        self.status_code = status_code
        self.text = text

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise AssertionError("Unexpected HTTP error in test response")


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self.response = response

    def get(self, url: str, timeout: float) -> DummyResponse:
        return self.response


class RobotsPolicyTests(unittest.TestCase):
    def test_404_allows_public_pages(self) -> None:
        policy = load_robots_policy(
            "https://books.example/",
            DummySession(DummyResponse(404)),
            "PortfolioBot/1.0",
            5.0,
        )
        self.assertEqual(policy.status, "not_found")
        self.assertTrue(policy.allows("https://books.example/catalogue/"))

    def test_rules_and_crawl_delay_are_applied(self) -> None:
        policy = load_robots_policy(
            "https://books.example/",
            DummySession(
                DummyResponse(
                    200,
                    "User-agent: *\nDisallow: /private/\nCrawl-delay: 2\n",
                )
            ),
            "PortfolioBot/1.0",
            5.0,
        )
        self.assertTrue(policy.allows("https://books.example/catalogue/"))
        self.assertFalse(policy.allows("https://books.example/private/"))
        self.assertEqual(policy.crawl_delay_seconds, 2.0)


if __name__ == "__main__":
    unittest.main()
