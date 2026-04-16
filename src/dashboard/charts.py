from __future__ import annotations

import re
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from analysis.summaries import explode_themes, add_roles


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def save_chart(path: Path) -> None:
    plt.tight_layout()
    plt.savefig(path, dpi=140, bbox_inches="tight")
    plt.close()


def make_charts(df: pd.DataFrame, summaries: dict[str, pd.DataFrame], charts_dir: str | Path) -> list[Path]:
    charts_dir = Path(charts_dir)
    charts_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []

    if df.empty:
        return created

    df = add_roles(df.copy())

    # ---------------------------
    # Overview charts
    # ---------------------------

    # Class sentiment
    plt.figure(figsize=(10, 5))
    t = summaries["class_summary"].sort_values("avg_sentiment", ascending=False)
    plt.bar(t["wow_class"], t["avg_sentiment"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Average Sentiment by Class")
    p = charts_dir / "overview_class_sentiment.png"
    save_chart(p)
    created.append(p)

    # Spec sentiment
    plt.figure(figsize=(12, 6))
    t = summaries["spec_summary"].sort_values("avg_sentiment", ascending=False).copy()
    t["label"] = t["spec"] + " (" + t["wow_class"] + ")"
    plt.bar(t["label"], t["avg_sentiment"])
    plt.xticks(rotation=60, ha="right")
    plt.title("Average Sentiment by Spec")
    p = charts_dir / "overview_spec_sentiment.png"
    save_chart(p)
    created.append(p)

    # Volume
    plt.figure(figsize=(10, 5))
    t = summaries["class_summary"].sort_values("records", ascending=False)
    plt.bar(t["wow_class"], t["records"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Discussion Volume by Class")
    p = charts_dir / "overview_class_volume.png"
    save_chart(p)
    created.append(p)

    # Sentiment buckets
    plt.figure(figsize=(6, 4))
    t = df["sentiment_bucket"].value_counts()
    plt.bar(t.index, t.values)
    plt.title("Sentiment Distribution")
    p = charts_dir / "overview_sentiment_buckets.png"
    save_chart(p)
    created.append(p)

    # Source sentiment (FIXED)
    plt.figure(figsize=(8, 5))
    t = summaries["subreddit_summary"].sort_values("avg_sentiment", ascending=False)
    plt.bar(t["source"], t["avg_sentiment"])
    plt.xticks(rotation=30, ha="right")
    plt.title("Average Sentiment by Source")
    p = charts_dir / "overview_source_sentiment.png"
    save_chart(p)
    created.append(p)

    # ---------------------------
    # Tier 2 Visuals
    # ---------------------------

    # Sentiment over time
    trend_df = df.copy()
    trend_df["created_iso"] = pd.to_datetime(trend_df["created_iso"], errors="coerce", utc=True)
    trend_df["month"] = trend_df["created_iso"].dt.strftime("%Y-%m")

    if not trend_df.empty:
        plt.figure(figsize=(10, 5))
        t = trend_df.groupby("month", as_index=False)["sentiment"].mean()
        plt.plot(t["month"], t["sentiment"], marker="o")
        plt.xticks(rotation=45, ha="right")
        plt.title("Average Sentiment Over Time")
        p = charts_dir / "overview_sentiment_over_time.png"
        save_chart(p)
        created.append(p)

    # Popularity vs sentiment
    popularity = df.groupby(["wow_class", "spec"], as_index=False).agg(
        mentions=("spec", "size"),
        avg_sentiment=("sentiment", "mean"),
    )

    if not popularity.empty:
        plt.figure(figsize=(9, 6))
        plt.scatter(popularity["mentions"], popularity["avg_sentiment"])

        for _, row in popularity.iterrows():
            label = f'{row["spec"]} ({row["wow_class"]})'
            plt.annotate(label, (row["mentions"], row["avg_sentiment"]), fontsize=7)

        plt.title("Popularity vs Sentiment")
        p = charts_dir / "overview_popularity_vs_sentiment.png"
        save_chart(p)
        created.append(p)

    # Role vs theme heatmap
    heat_df = df.copy()
    heat_df["themes"] = heat_df["themes"].fillna("").str.split(",")
    heat_df = heat_df.explode("themes")
    heat_df["themes"] = heat_df["themes"].str.strip()
    heat_df = heat_df[heat_df["themes"] != ""]

    if not heat_df.empty:
        pivot = heat_df.groupby(["role", "themes"]).size().unstack(fill_value=0)

        plt.figure(figsize=(12, 5))
        plt.imshow(pivot.values, aspect="auto")

        plt.xticks(range(len(pivot.columns)), pivot.columns, rotation=45, ha="right")
        plt.yticks(range(len(pivot.index)), pivot.index)

        for i in range(len(pivot.index)):
            for j in range(len(pivot.columns)):
                plt.text(j, i, str(pivot.iloc[i, j]), ha="center", va="center", fontsize=7)

        plt.title("Role vs Theme Heatmap")
        p = charts_dir / "overview_role_theme_heatmap.png"
        save_chart(p)
        created.append(p)

    # ---------------------------
    # Class-level charts
    # ---------------------------

    theme_df = explode_themes(df)

    for wow_class in df["wow_class"].dropna().unique():
        cdf = df[df["wow_class"] == wow_class]

        plt.figure(figsize=(8, 4))
        t = cdf.groupby("spec", as_index=False)["sentiment"].mean()
        plt.bar(t["spec"], t["sentiment"])
        plt.xticks(rotation=30)
        plt.title(f"{wow_class} Spec Sentiment")
        p = charts_dir / f"class_{slugify(wow_class)}_sentiment.png"
        save_chart(p)
        created.append(p)

        ctheme = theme_df[theme_df["wow_class"] == wow_class]
        if not ctheme.empty:
            plt.figure(figsize=(8, 4))
            t = ctheme["theme"].value_counts().head(10)
            plt.bar(t.index, t.values)
            plt.xticks(rotation=30)
            plt.title(f"{wow_class} Themes")
            p = charts_dir / f"class_{slugify(wow_class)}_themes.png"
            save_chart(p)
            created.append(p)

    return created