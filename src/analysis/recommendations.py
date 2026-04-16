from __future__ import annotations

import pandas as pd


def recommend_action(avg_sentiment: float, top_themes: list[str], role: str) -> str:
    theme_text = ", ".join(top_themes[:3]) if top_themes else "general sentiment"

    if avg_sentiment <= -0.35:
        if "Rotation" in top_themes or "Complexity" in top_themes:
            return f"Review rotational friction and complexity for this {role.lower()} spec, especially around {theme_text}."
        if "Mobility" in top_themes:
            return f"Investigate mobility pain points for this {role.lower()} spec and evaluate movement tools or encounter friction."
        if "Survivability" in top_themes:
            return f"Evaluate defensive uptime and survivability complaints for this {role.lower()} spec."
        if "Damage" in top_themes or "Healing" in top_themes:
            return f"Review performance perception around {theme_text} and compare player sentiment to actual balance data."
        return f"Investigate negative community sentiment around {theme_text} and identify the main gameplay pain points."

    if avg_sentiment >= 0.35:
        if "Utility" in top_themes or "Fun" in top_themes:
            return f"Preserve the spec identity around {theme_text}, since these appear to drive positive player sentiment."
        if "Damage" in top_themes or "Healing" in top_themes:
            return f"Maintain the strengths around {theme_text} while watching for future balance drift."
        return f"Preserve the positive aspects of {theme_text} while monitoring for overperformance or future complaints."

    if "Rotation" in top_themes or "Complexity" in top_themes:
        return f"Consider a small usability pass on {theme_text} to reduce friction without removing mastery."
    if "Fun" in top_themes and "Damage" in top_themes:
        return f"Keep the core gameplay loop intact, but monitor whether strengths in {theme_text} remain satisfying over time."
    return f"Monitor mixed player sentiment around {theme_text} and gather more feedback before proposing major changes."


def generate_recommendations(summaries: dict[str, pd.DataFrame]) -> pd.DataFrame:
    spec_summary = summaries["spec_summary"]
    spec_theme_summary = summaries["spec_theme_summary"]

    recommendations: list[dict[str, str | float | int]] = []

    for _, row in spec_summary.iterrows():
        wow_class = row["wow_class"]
        spec = row["spec"]
        role = row["role"]
        avg_sentiment = float(row["avg_sentiment"])
        records = int(row["records"])

        spec_themes = spec_theme_summary[
            (spec_theme_summary["wow_class"] == wow_class) &
            (spec_theme_summary["spec"] == spec)
        ].sort_values("count", ascending=False)

        top_themes = spec_themes["theme"].head(3).tolist()
        recommendation = recommend_action(avg_sentiment, top_themes, role)

        if avg_sentiment >= 0.35:
            priority = "Low"
        elif avg_sentiment <= -0.35:
            priority = "High"
        else:
            priority = "Medium"

        recommendations.append({
            "wow_class": wow_class,
            "spec": spec,
            "role": role,
            "avg_sentiment": avg_sentiment,
            "records": records,
            "top_themes": ", ".join(top_themes),
            "priority": priority,
            "recommendation": recommendation,
        })

    rec_df = pd.DataFrame(recommendations)
    if not rec_df.empty:
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        rec_df["_priority_sort"] = rec_df["priority"].map(priority_order)
        rec_df = rec_df.sort_values(
            ["_priority_sort", "avg_sentiment", "records"],
            ascending=[True, True, False]
        ).drop(columns="_priority_sort").reset_index(drop=True)

    return rec_df