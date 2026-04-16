from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from analysis.sentiment import sentiment_bucket, sentiment_score
from analysis.themes import detect_themes


REQUIRED_COLUMNS = [
    "wow_class",
    "spec",
    "source_type",
    "author",
    "created_iso",
    "score",
    "url",
    "title",
    "body",
    "combined_text",
]


def load_json_records(path: str | Path) -> pd.DataFrame:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        records = json.load(f)

    df = pd.DataFrame(records)

    # backwards compatibility
    if "source" not in df.columns and "subreddit" in df.columns:
        df["source"] = df["subreddit"]

    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in input JSON: {missing}")

    if "source" not in df.columns:
        df["source"] = "unknown"

    df["sentiment"] = df["combined_text"].astype(str).apply(sentiment_score)
    df["sentiment_bucket"] = df["sentiment"].apply(sentiment_bucket)
    df["themes"] = df["combined_text"].astype(str).apply(lambda text: ",".join(detect_themes(text)))
    return df