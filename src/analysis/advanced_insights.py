from __future__ import annotations

import pandas as pd


def classify_risk_level(avg_sentiment: float, records: int) -> str:
    if avg_sentiment <= -0.35 and records >= 3:
        return "High"
    if avg_sentiment <= 0 and records >= 2:
        return "Medium"
    return "Low"


def prioritize_specs(spec_summary: pd.DataFrame) -> pd.DataFrame:
    if spec_summary.empty:
        return pd.DataFrame()

    out = spec_summary.copy()
    out["risk_level"] = out.apply(
        lambda row: classify_risk_level(float(row["avg_sentiment"]), int(row["records"])),
        axis=1,
    )
    return out.sort_values(["risk_level", "avg_sentiment", "records"], ascending=[True, True, False])