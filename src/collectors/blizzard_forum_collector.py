from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Iterable

import pandas as pd
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

BASE_FORUM = "https://us.forums.blizzard.com/en/wow"


@dataclass
class ForumRecord:
    wow_class: str
    spec: str
    source_type: str
    source: str
    author: str
    created_iso: str
    score: int
    url: str
    title: str
    body: str
    combined_text: str


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", str(text))
    return text.strip()


def fetch_json(url: str) -> dict:
    response = requests.get(url, headers=HEADERS, timeout=20)
    response.raise_for_status()
    return response.json()


def build_topic_url(slug: str, topic_id: int) -> str:
    return f"{BASE_FORUM}/t/{slug}/{topic_id}"


def build_topic_json_url(slug: str, topic_id: int) -> str:
    return f"{BASE_FORUM}/t/{slug}/{topic_id}.json"


def infer_spec_from_title(title: str, wow_class: str) -> str:
    """
    Lightweight keyword-based spec inference.
    Falls back to class-level 'Unknown' if not detected.
    """
    title_l = title.lower()

    spec_map = {
        "Death Knight": {
            "blood": "Blood",
            "frost": "Frost",
            "unholy": "Unholy",
            "uhdk": "Unholy",
        },
        "Demon Hunter": {
            "havoc": "Havoc",
            "vengeance": "Vengeance",
            "devourer": "Devourer",
        },
        "Druid": {
            "balance": "Balance",
            "boomkin": "Balance",
            "feral": "Feral",
            "guardian": "Guardian",
            "resto": "Restoration",
            "restoration": "Restoration",
        },
        "Evoker": {
            "devastation": "Devastation",
            "preservation": "Preservation",
            "augmentation": "Augmentation",
            "aug": "Augmentation",
            "pres": "Preservation",
            "dev": "Devastation",
        },
        "Hunter": {
            "beast mastery": "Beast Mastery",
            "bm": "Beast Mastery",
            "marksmanship": "Marksmanship",
            "mm": "Marksmanship",
            "survival": "Survival",
            "sv": "Survival",
        },
        "Mage": {
            "arcane": "Arcane",
            "fire": "Fire",
            "frost": "Frost",
        },
        "Monk": {
            "brewmaster": "Brewmaster",
            "mistweaver": "Mistweaver",
            "windwalker": "Windwalker",
            "mw": "Mistweaver",
            "ww": "Windwalker",
            "brm": "Brewmaster",
        },
        "Paladin": {
            "holy": "Holy",
            "protection": "Protection",
            "prot": "Protection",
            "retribution": "Retribution",
            "ret": "Retribution",
        },
        "Priest": {
            "discipline": "Discipline",
            "disc": "Discipline",
            "holy": "Holy",
            "shadow": "Shadow",
            "spriest": "Shadow",
        },
        "Rogue": {
            "assassination": "Assassination",
            "assa": "Assassination",
            "outlaw": "Outlaw",
            "subtlety": "Subtlety",
            "sub": "Subtlety",
        },
        "Shaman": {
            "elemental": "Elemental",
            "enhancement": "Enhancement",
            "enh": "Enhancement",
            "resto": "Restoration",
            "restoration": "Restoration",
        },
        "Warlock": {
            "affliction": "Affliction",
            "demonology": "Demonology",
            "demo": "Demonology",
            "destruction": "Destruction",
            "destro": "Destruction",
        },
        "Warrior": {
            "arms": "Arms",
            "fury": "Fury",
            "protection": "Protection",
            "prot": "Protection",
        },
    }

    class_specs = spec_map.get(wow_class, {})
    for needle, spec_name in class_specs.items():
        if needle in title_l:
            return spec_name

    return "Unknown"


def category_name_to_class(category_name: str) -> str:
    """
    Blizzard class forum category labels match class names on the class forum page.
    """
    return clean_text(category_name)


def collect_class_topics_from_category_json(
    category_json_url: str,
    max_topics: int = 25,
) -> list[dict]:
    """
    Reads the Blizzard class category JSON endpoint and returns topic metadata rows.
    """
    payload = fetch_json(category_json_url)

    topic_list = payload.get("topic_list", {})
    topics = topic_list.get("topics", [])

    out: list[dict] = []
    for topic in topics[:max_topics]:
        title = clean_text(topic.get("title", ""))
        slug = topic.get("slug", "")
        topic_id = int(topic.get("id"))
        created_at = topic.get("created_at", "")
        replies = int(topic.get("reply_count", 0))
        views = int(topic.get("views", 0))
        category_id = topic.get("category_id", None)

        posters = topic.get("posters", [])
        author = "unknown"
        if posters:
            author = posters[0].get("description", "unknown")

        out.append(
            {
                "title": title,
                "slug": slug,
                "topic_id": topic_id,
                "created_iso": created_at,
                "reply_count": replies,
                "views": views,
                "category_id": category_id,
                "url": build_topic_url(slug, topic_id),
                "topic_json_url": build_topic_json_url(slug, topic_id),
                "author": author,
            }
        )

    return out


def collect_posts_from_topic_json(
    topic_json_url: str,
    wow_class: str,
    spec: str,
    source_name: str = "blizzard_forums",
) -> list[ForumRecord]:
    """
    Reads a topic .json endpoint and emits one record per post.
    """
    payload = fetch_json(topic_json_url)

    title = clean_text(payload.get("title", "Untitled Thread"))
    post_stream = payload.get("post_stream", {})
    posts = post_stream.get("posts", [])

    records: list[ForumRecord] = []
    for post in posts:
        cooked = clean_text(post.get("cooked", ""))
        cooked = re.sub(r"<[^>]+>", " ", cooked)
        cooked = clean_text(cooked)

        if len(cooked) < 20:
            continue

        author = clean_text(post.get("username", "unknown"))
        created_iso = post.get("created_at", "")
        post_number = int(post.get("post_number", 0))

        body = cooked[:4000]
        combined = clean_text(f"{title}. {body}")
        base_url = payload.get("slug", "")
        topic_id = int(payload.get("id"))
        url = f"{BASE_FORUM}/t/{base_url}/{topic_id}/{post_number}"

        records.append(
            ForumRecord(
                wow_class=wow_class,
                spec=spec,
                source_type="thread_post",
                source=source_name,
                author=author,
                created_iso=created_iso,
                score=0,
                url=url,
                title=title,
                body=body,
                combined_text=combined,
            )
        )

    return records


def auto_collect_from_classes_feed(
    category_json_url: str,
    max_topics: int = 25,
    allowed_classes: Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Pull topics from the main Classes JSON feed, infer class/spec,
    then pull individual posts from each topic JSON endpoint.
    """
    topics = collect_class_topics_from_category_json(category_json_url, max_topics=max_topics)

    allowed = set(allowed_classes or [])
    all_records: list[dict] = []

    # Known class names visible in the Classes forum
    known_classes = {
        "Priest", "Rogue", "Monk", "Paladin", "Death Knight", "Evoker",
        "Hunter", "Warrior", "Shaman", "Demon Hunter", "Druid", "Warlock", "Mage",
    }

    for topic in topics:
        title = topic["title"]

        wow_class = "Unknown"
        for candidate in known_classes:
            if candidate.lower() in title.lower():
                wow_class = candidate
                break

        # If class wasn't in the title, leave it Unknown for now
        if wow_class == "Unknown":
            continue

        if allowed and wow_class not in allowed:
            continue

        spec = infer_spec_from_title(title, wow_class)

        try:
            records = collect_posts_from_topic_json(
                topic_json_url=topic["topic_json_url"],
                wow_class=wow_class,
                spec=spec,
            )
            all_records.extend(asdict(r) for r in records)
            print(f"[info] {wow_class}/{spec}: collected {len(records)} posts from {topic['url']}")
        except Exception as exc:
            print(f"[warn] Failed topic {topic['url']}: {exc}")

    return pd.DataFrame(all_records)