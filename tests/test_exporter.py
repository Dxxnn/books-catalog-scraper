import json
import tempfile
import unittest
from pathlib import Path

from books_catalog_scraper.exporter import (
    build_summary,
    export_results,
    records_to_frame,
)
from books_catalog_scraper.models import BookRecord


class ExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.records = [
            BookRecord(
                title="  Book   B ",
                price_gbp=20.0,
                availability="In stock",
                in_stock=True,
                rating=5,
                product_url="https://books.example/b",
                source_page=1,
                scraped_at_utc="2026-07-26T12:00:00+00:00",
            ),
            BookRecord(
                title="Book A",
                price_gbp=10.0,
                availability="Out of stock",
                in_stock=False,
                rating=3,
                product_url="https://books.example/a",
                source_page=1,
                scraped_at_utc="2026-07-26T12:00:00+00:00",
            ),
        ]

    def test_cleans_and_summarizes_records(self) -> None:
        frame = records_to_frame(self.records)
        self.assertEqual(frame["title"].tolist(), ["Book A", "Book B"])
        summary = build_summary(frame)
        self.assertEqual(summary["record_count"], 2)
        self.assertEqual(summary["in_stock_count"], 1)
        self.assertEqual(summary["price_gbp"]["mean"], 15.0)

    def test_exports_csv_and_json(self) -> None:
        frame = records_to_frame(self.records)
        with tempfile.TemporaryDirectory() as directory:
            paths = export_results(frame, Path(directory))
            self.assertTrue(paths["csv"].is_file())
            self.assertTrue(paths["json"].is_file())
            summary = json.loads(
                paths["summary"].read_text(encoding="utf-8")
            )
        self.assertEqual(summary["record_count"], 2)


if __name__ == "__main__":
    unittest.main()
