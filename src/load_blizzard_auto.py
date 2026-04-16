from __future__ import annotations

from pathlib import Path

from collectors.blizzard_forum_collector import auto_collect_from_classes_feed


def main() -> None:
    category_json_url = "https://us.forums.blizzard.com/en/wow/c/classes/174.json"

    df = auto_collect_from_classes_feed(
        category_json_url=category_json_url,
        max_topics=20,
        allowed_classes=None,  # Example: ["Priest", "Evoker", "Hunter"]
    )

    out_path = Path("data/blizzard_auto_threads.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")

    print(f"Saved {len(df)} records to {out_path}")


if __name__ == "__main__":
    main()