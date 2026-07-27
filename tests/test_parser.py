from pathlib import Path
import unittest

from books_catalog_scraper.parser import (
    CatalogueParseError,
    parse_catalogue_page,
)


FIXTURE = Path(__file__).parent / "fixtures" / "catalogue_page.html"


class CatalogueParserTests(unittest.TestCase):
    def test_extracts_records_and_next_page(self) -> None:
        records, next_url = parse_catalogue_page(
            FIXTURE.read_text(encoding="utf-8"),
            "https://books.example/",
            page_number=1,
            scraped_at_utc="2026-07-26T12:00:00+00:00",
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(records[0].title, "Example One")
        self.assertEqual(records[0].price_gbp, 12.34)
        self.assertTrue(records[0].in_stock)
        self.assertEqual(records[0].rating, 3)
        self.assertEqual(records[1].title, "Example Two")
        self.assertFalse(records[1].in_stock)
        self.assertEqual(
            next_url,
            "https://books.example/catalogue/page-2.html",
        )

    def test_rejects_page_without_catalogue_cards(self) -> None:
        with self.assertRaises(CatalogueParseError):
            parse_catalogue_page(
                "<html><body></body></html>",
                "https://books.example/",
                page_number=1,
            )


if __name__ == "__main__":
    unittest.main()
