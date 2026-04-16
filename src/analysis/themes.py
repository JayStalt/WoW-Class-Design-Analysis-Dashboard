from __future__ import annotations

THEME_KEYWORDS = {
    "Damage": ["damage", "dps", "burst", "aoe", "cleave", "single target", "st", "execute"],
    "Healing": ["healing", "healer", "heal", "throughput", "hps", "spot heal", "raid heal"],
    "Utility": ["utility", "buff", "dispel", "dispell", "interrupt", "cc", "battle rez", "lust"],
    "Mobility": ["mobility", "movement", "mobile", "dash", "slow", "stuck"],
    "Survivability": ["survivability", "tanky", "squishy", "defensive", "survive", "durable"],
    "Rotation": ["rotation", "priority", "button bloat", "bloat", "apm", "opener", "loop"],
    "Complexity": ["hard", "easy", "simple", "complex", "skill ceiling", "skill floor", "punishing"],
    "Fun": ["fun", "boring", "enjoy", "enjoyable", "satisfying", "unfun", "fantasy"],
    "Meta": ["meta", "viable", "competitive", "bench", "pick rate", "best", "worst"],
}


def detect_themes(text: str) -> list[str]:
    lower_text = text.lower()
    found = []
    for theme, keywords in THEME_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            found.append(theme)
    return found