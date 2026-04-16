from __future__ import annotations

import pandas as pd


ROLE_MAP = {
    ("Death Knight", "Blood"): "Tank",
    ("Death Knight", "Frost"): "DPS",
    ("Death Knight", "Unholy"): "DPS",

    ("Demon Hunter", "Havoc"): "DPS",
    ("Demon Hunter", "Vengeance"): "Tank",
    ("Demon Hunter", "Devourer"): "DPS",

    ("Druid", "Balance"): "DPS",
    ("Druid", "Feral"): "DPS",
    ("Druid", "Guardian"): "Tank",
    ("Druid", "Restoration"): "Healer",

    ("Evoker", "Devastation"): "DPS",
    ("Evoker", "Preservation"): "Healer",
    ("Evoker", "Augmentation"): "DPS",

    ("Hunter", "Beast Mastery"): "DPS",
    ("Hunter", "Marksmanship"): "DPS",
    ("Hunter", "Survival"): "DPS",

    ("Mage", "Arcane"): "DPS",
    ("Mage", "Fire"): "DPS",
    ("Mage", "Frost"): "DPS",

    ("Monk", "Brewmaster"): "Tank",
    ("Monk", "Mistweaver"): "Healer",
    ("Monk", "Windwalker"): "DPS",

    ("Paladin", "Holy"): "Healer",
    ("Paladin", "Protection"): "Tank",
    ("Paladin", "Retribution"): "DPS",

    ("Priest", "Discipline"): "Healer",
    ("Priest", "Holy"): "Healer",
    ("Priest", "Shadow"): "DPS",

    ("Rogue", "Assassination"): "DPS",
    ("Rogue", "Outlaw"): "DPS",
    ("Rogue", "Subtlety"): "DPS",

    ("Shaman", "Elemental"): "DPS",
    ("Shaman", "Enhancement"): "DPS",
    ("Shaman", "Restoration"): "Healer",

    ("Warlock", "Affliction"): "DPS",
    ("Warlock", "Demonology"): "DPS",
    ("Warlock", "Destruction"): "DPS",

    ("Warrior", "Arms"): "DPS",
    ("Warrior", "Fury"): "DPS",
    ("Warrior", "Protection"): "Tank",
}


def add_roles(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["role"] = df.apply(
        lambda row: ROLE_MAP.get((row["wow_class"], row["spec"]), "Unknown"),
        axis=1
    )
    return df


def explode_themes(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["wow_class", "spec", "role", "theme", "sentiment_bucket"])

    temp = df[["wow_class", "spec", "role", "themes", "sentiment_bucket"]].copy()
    temp["themes"] = temp["themes"].fillna("")
    temp["theme"] = temp["themes"].str.split(",")
    temp = temp.explode("theme")
    temp["theme"] = temp["theme"].fillna("").str.strip()
    return temp[temp["theme"] != ""][["wow_class", "spec", "role", "theme", "sentiment_bucket"]]


def build_summary_tables(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    if df.empty:
        empty = pd.DataFrame()
        return {
            "overview": empty,
            "role_summary": empty,
            "class_summary": empty,
            "spec_summary": empty,
            "subreddit_summary": empty,
            "theme_summary": empty,
            "top_loved_specs": empty,
            "top_complained_specs": empty,
            "class_theme_summary": empty,
            "spec_theme_summary": empty,
            "positive_theme_summary": empty,
            "negative_theme_summary": empty,
        }

    df = add_roles(df)

    overview = pd.DataFrame([{
        "records": len(df),
        "classes": df["wow_class"].nunique(),
        "specs": df["spec"].nunique(),
        "roles": df["role"].nunique(),
        "avg_sentiment": round(df["sentiment"].mean(), 3),
        "positive_pct": round((df["sentiment_bucket"] == "Positive").mean() * 100, 2),
        "negative_pct": round((df["sentiment_bucket"] == "Negative").mean() * 100, 2),
        "mixed_pct": round((df["sentiment_bucket"] == "Mixed/Neutral").mean() * 100, 2),
        "avg_score": round(df["score"].mean(), 2),
    }])

    role_summary = df.groupby("role", as_index=False).agg(
        records=("role", "size"),
        avg_sentiment=("sentiment", "mean"),
        avg_score=("score", "mean"),
        positive_pct=("sentiment_bucket", lambda s: s.eq("Positive").mean() * 100),
        negative_pct=("sentiment_bucket", lambda s: s.eq("Negative").mean() * 100),
        mixed_pct=("sentiment_bucket", lambda s: s.eq("Mixed/Neutral").mean() * 100),
    ).sort_values(["avg_sentiment", "records"], ascending=[False, False])

    class_summary = df.groupby(["wow_class", "role"], as_index=False).agg(
        records=("wow_class", "size"),
        avg_sentiment=("sentiment", "mean"),
        avg_score=("score", "mean"),
        positive_pct=("sentiment_bucket", lambda s: s.eq("Positive").mean() * 100),
        negative_pct=("sentiment_bucket", lambda s: s.eq("Negative").mean() * 100),
        mixed_pct=("sentiment_bucket", lambda s: s.eq("Mixed/Neutral").mean() * 100),
    ).sort_values(["avg_sentiment", "records"], ascending=[False, False])

    spec_summary = df.groupby(["wow_class", "spec", "role"], as_index=False).agg(
        records=("spec", "size"),
        avg_sentiment=("sentiment", "mean"),
        avg_score=("score", "mean"),
        positive_pct=("sentiment_bucket", lambda s: s.eq("Positive").mean() * 100),
        negative_pct=("sentiment_bucket", lambda s: s.eq("Negative").mean() * 100),
        mixed_pct=("sentiment_bucket", lambda s: s.eq("Mixed/Neutral").mean() * 100),
    ).sort_values(["avg_sentiment", "records"], ascending=[False, False])

    source_summary = df.groupby("source", as_index=False).agg(
        records=("source", "size"),
        avg_sentiment=("sentiment", "mean"),
        avg_score=("score", "mean"),
    ).sort_values("records", ascending=False)

    theme_df = explode_themes(df)

    if theme_df.empty:
        theme_summary = pd.DataFrame(columns=["wow_class", "spec", "role", "theme", "count"])
        class_theme_summary = pd.DataFrame(columns=["wow_class", "role", "theme", "count"])
        spec_theme_summary = pd.DataFrame(columns=["wow_class", "spec", "role", "theme", "count"])
        positive_theme_summary = pd.DataFrame(columns=["theme", "count"])
        negative_theme_summary = pd.DataFrame(columns=["theme", "count"])
    else:
        theme_summary = (
            theme_df.groupby(["wow_class", "spec", "role", "theme"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values(["wow_class", "spec", "count"], ascending=[True, True, False])
        )

        class_theme_summary = (
            theme_df.groupby(["wow_class", "role", "theme"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values(["wow_class", "count"], ascending=[True, False])
        )

        spec_theme_summary = (
            theme_df.groupby(["wow_class", "spec", "role", "theme"], as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values(["wow_class", "spec", "count"], ascending=[True, True, False])
        )

        positive_theme_summary = (
            theme_df[theme_df["sentiment_bucket"] == "Positive"]
            .groupby("theme", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
        )

        negative_theme_summary = (
            theme_df[theme_df["sentiment_bucket"] == "Negative"]
            .groupby("theme", as_index=False)
            .size()
            .rename(columns={"size": "count"})
            .sort_values("count", ascending=False)
        )

    eligible_specs = spec_summary[spec_summary["records"] >= 1].copy()

    top_loved_specs = (
        eligible_specs.sort_values(["avg_sentiment", "records"], ascending=[False, False])
        .head(5)
        .reset_index(drop=True)
    )

    top_complained_specs = (
        eligible_specs.sort_values(["avg_sentiment", "records"], ascending=[True, False])
        .head(5)
        .reset_index(drop=True)
    )

    return {
        "overview": overview,
        "role_summary": role_summary,
        "class_summary": class_summary,
        "spec_summary": spec_summary,
        "subreddit_summary": source_summary,
        "theme_summary": theme_summary,
        "top_loved_specs": top_loved_specs,
        "top_complained_specs": top_complained_specs,
        "class_theme_summary": class_theme_summary,
        "spec_theme_summary": spec_theme_summary,
        "positive_theme_summary": positive_theme_summary,
        "negative_theme_summary": negative_theme_summary,
    }