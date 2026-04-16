from __future__ import annotations

import pandas as pd


def collect_from_reddit(*args, **kwargs) -> pd.DataFrame:
    raise NotImplementedError(
        "Reddit collector is intentionally disabled in phase 1. "
        "Use file_collector.load_json_records() with sample/local data for now."
    )