from __future__ import annotations

import math
import re

POSITIVE_WORDS = {
    "good", "great", "strong", "fun", "smooth", "rewarding", "powerful", "viable",
    "solid", "amazing", "love", "loved", "best", "meta", "clean", "fluid",
    "competitive", "enjoyable", "reliable", "fantastic", "clutch", "versatile",
    "useful", "buffed", "buff"
}

NEGATIVE_WORDS = {
    "bad", "weak", "terrible", "awful", "clunky", "boring", "underwhelming", "useless",
    "nerf", "nerfed", "squishy", "slow", "dead", "worse", "worst", "rough", "painful",
    "frustrating", "bugged", "broken", "unfun", "garbage", "trash", "mediocre",
    "punishing", "inconsistent", "stale", "janky", "annoying", "gutted", "bloat", "bloated"
}

INTENSIFIERS = {"very", "really", "super", "extremely", "insanely", "so"}
NEGATORS = {"not", "never", "hardly", "barely", "isn't", "wasn't", "don't", "doesn't", "cant", "can't"}


def tokenize(text: str) -> list[str]:
    return re.findall(r"[a-zA-Z][a-zA-Z\-']+", text.lower())


def sentiment_score(text: str) -> float:
    tokens = tokenize(text)
    if not tokens:
        return 0.0

    total = 0.0
    for i, token in enumerate(tokens):
        mult = 1.0
        if i > 0 and tokens[i - 1] in INTENSIFIERS:
            mult *= 1.5

        negated = i > 0 and tokens[i - 1] in NEGATORS
        if token in POSITIVE_WORDS:
            total += (-1 if negated else 1) * mult
        elif token in NEGATIVE_WORDS:
            total += (1 if negated else -1) * mult

    divisor = max(1.0, math.log(len(tokens) + 1, 10) * 2)
    return round(total / divisor, 3)


def sentiment_bucket(score: float) -> str:
    if score >= 0.35:
        return "Positive"
    if score <= -0.35:
        return "Negative"
    return "Mixed/Neutral"