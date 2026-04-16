from __future__ import annotations

import pandas as pd


def generate_insights(df: pd.DataFrame, summaries: dict[str, pd.DataFrame]) -> pd.DataFrame:
    insights = []

    spec_summary = summaries["spec_summary"]
    theme_summary = summaries["spec_theme_summary"]

    for _, row in spec_summary.iterrows():
        wow_class = row["wow_class"]
        spec = row["spec"]
        sentiment = row["avg_sentiment"]

        spec_themes = theme_summary[
            (theme_summary["wow_class"] == wow_class) &
            (theme_summary["spec"] == spec)
        ].sort_values("count", ascending=False)

        top_themes = spec_themes.head(3)["theme"].tolist()

        if sentiment >= 0.35:
            tone = "positive"
        elif sentiment <= -0.35:
            tone = "negative"
        else:
            tone = "mixed"

        insight = f"{spec} {wow_class} shows {tone} sentiment"

        if top_themes:
            insight += f" driven by {', '.join(top_themes)}"

        if tone == "negative":
            insight += ", suggesting potential design friction."
        elif tone == "positive":
            insight += ", indicating strong player satisfaction."
        else:
            insight += ", with both strengths and weaknesses."

        insights.append({
            "wow_class": wow_class,
            "spec": spec,
            "insight": insight
        })

    return pd.DataFrame(insights)