"""Data cleaning, export and descriptive summary."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

import pandas as pd

from .models import BookRecord


OUTPUT_COLUMNS = [
    "title",
    "price_gbp",
    "availability",
    "in_stock",
    "rating",
    "product_url",
    "source_page",
    "scraped_at_utc",
]


def records_to_frame(records: list[BookRecord]) -> pd.DataFrame:
    if not records:
        return pd.DataFrame(columns=OUTPUT_COLUMNS)

    frame = pd.DataFrame(asdict(record) for record in records)
    frame["title"] = frame["title"].astype(str).str.replace(
        r"\s+", " ", regex=True
    ).str.strip()
    frame["availability"] = frame["availability"].astype(str).str.replace(
        r"\s+", " ", regex=True
    ).str.strip()
    frame["price_gbp"] = pd.to_numeric(frame["price_gbp"], errors="raise").round(2)
    frame["rating"] = pd.to_numeric(
        frame["rating"], errors="raise", downcast="integer"
    )
    frame["source_page"] = pd.to_numeric(
        frame["source_page"], errors="raise", downcast="integer"
    )
    frame["in_stock"] = frame["in_stock"].astype(bool)
    frame = frame.drop_duplicates(subset=["product_url"], keep="first")
    frame = frame.sort_values(
        by=["source_page", "title"], kind="stable"
    ).reset_index(drop=True)
    return frame[OUTPUT_COLUMNS]


def build_summary(frame: pd.DataFrame) -> dict[str, object]:
    if frame.empty:
        return {
            "record_count": 0,
            "in_stock_count": 0,
            "price_gbp": None,
            "rating_distribution": {},
        }

    ratings = (
        frame["rating"]
        .value_counts()
        .sort_index()
        .rename_axis("rating")
        .to_dict()
    )
    return {
        "record_count": int(len(frame)),
        "in_stock_count": int(frame["in_stock"].sum()),
        "price_gbp": {
            "min": round(float(frame["price_gbp"].min()), 2),
            "mean": round(float(frame["price_gbp"].mean()), 2),
            "max": round(float(frame["price_gbp"].max()), 2),
        },
        "rating_distribution": {
            str(int(rating)): int(count) for rating, count in ratings.items()
        },
    }


def export_results(
    frame: pd.DataFrame,
    output_dir: Path,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "books.csv"
    json_path = output_dir / "books.json"
    summary_path = output_dir / "summary.json"

    frame.to_csv(csv_path, index=False, encoding="utf-8")
    frame.to_json(
        json_path,
        orient="records",
        indent=2,
        force_ascii=False,
    )
    summary_path.write_text(
        json.dumps(build_summary(frame), indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "csv": csv_path,
        "json": json_path,
        "summary": summary_path,
    }
