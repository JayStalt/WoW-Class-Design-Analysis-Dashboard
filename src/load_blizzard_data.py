from __future__ import annotations

import json
from pathlib import Path

from collectors.blizzard_forum_collector import collect_blizzard_threads


def main() -> None:
    thread_configs = [
        {
            "url": "https://us.forums.blizzard.com/en/wow/t/preservation-mana-issues/2109411",
            "wow_class": "Evoker",
            "spec": "Preservation",
        },
        {
            "url": "https://us.forums.blizzard.com/en/wow/t/disc-priest-atonement-healing-nerfed-again/2109476",
            "wow_class": "Priest",
            "spec": "Discipline",
        },
        {
            "url": "https://us.forums.blizzard.com/en/wow/t/bm-hunters-pack-leader-need-to-be-buffed/2109531",
            "wow_class": "Hunter",
            "spec": "Beast Mastery",
        },
    ]

    df = collect_blizzard_threads(thread_configs)

    out_path = Path("data/blizzard_forum_threads.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(df.to_json(orient="records", indent=2), encoding="utf-8")

    print(f"Saved {len(df)} records to {out_path}")


if __name__ == "__main__":
    main()