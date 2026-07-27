import unittest

from books_catalog_scraper.config import ScraperConfig


class ConfigTests(unittest.TestCase):
    def test_rejects_unsafe_delay(self) -> None:
        with self.assertRaises(ValueError):
            ScraperConfig(delay_seconds=0.1).validate()

    def test_rejects_excessive_page_count(self) -> None:
        with self.assertRaises(ValueError):
            ScraperConfig(max_pages=51).validate()

    def test_accepts_default_configuration(self) -> None:
        self.assertIsInstance(ScraperConfig().validate(), ScraperConfig)


if __name__ == "__main__":
    unittest.main()
