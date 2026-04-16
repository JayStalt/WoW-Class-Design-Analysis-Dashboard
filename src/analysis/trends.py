from __future__ import annotations

import pandas as pd

from analysis.summaries import add_roles


def build_time_trends(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = df.copy()
    df["created_iso"] = pd.to_datetime(df["created_iso"], errors="coerce", utc=True)
    df["month"] = df["created_iso"].dt.strftime("%Y-%m")

    trends = df.groupby(["month", "wow_class", "spec"], as_index=False).agg(
        avg_sentiment=("sentiment", "mean"),
        records=("spec", "size")
    )

    return trends.sort_values(["month", "avg_sentiment"], ascending=[True, False])


def build_popularity(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    popularity = df.groupby(["wow_class", "spec"], as_index=False).agg(
        mentions=("spec", "size"),
        avg_sentiment=("sentiment", "mean")
    )

    return popularity.sort_values("mentions", ascending=False)


def build_role_theme_matrix(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()

    df = add_roles(df.copy())
    df["themes"] = df["themes"].fillna("").str.split(",")
    df = df.explode("themes")
    df["themes"] = df["themes"].fillna("").str.strip()
    df = df[df["themes"] != ""]

    matrix = (
        df.groupby(["role", "themes"], as_index=False)
        .size()
        .rename(columns={"size": "count"})
        .sort_values(["role", "count"], ascending=[True, False])
    )

    return matrix