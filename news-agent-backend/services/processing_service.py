from datetime import datetime, timezone
from dateutil import parser
import re


def parse_date(date_str: str):
    """
    Tries to parse RSS dates + ISO dates safely.
    Returns datetime in UTC or None.
    """
    if not date_str:
        return None
    try:
        dt = parser.parse(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def filter_by_date_range(articles, from_date: str, to_date: str):
    start = parse_date(from_date)
    end = parse_date(to_date)

    if not start or not end:
        return articles

    filtered = []
    for a in articles:
        pub = parse_date(a.get("publishedAt", ""))
        if not pub:
            continue

        if start <= pub <= end:
            filtered.append(a)

    return filtered



def normalize_title(title: str):
    t = (title or "").lower().strip()
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t)
    return t


def deduplicate_articles(articles):
    """
    Simple dedup based on normalized title similarity.
    Returns:
      - merged_articles (unique list)
    """
    seen = {}
    merged = []

    for a in articles:
        key = normalize_title(a.get("title", ""))

        if not key:
            continue

        if key in seen:
            # duplicate found
            original = seen[key]
            original["coverageCount"] = original.get("coverageCount", 1) + 1
            original["isDuplicateGroup"] = True
        else:
            seen[key] = a
            merged.append(a)

    return merged

CREDIBILITY_WEIGHTS = {
    "Reuters": 5,
    "BBC": 4,
    "TechCrunch": 3,
    "Times of India": 2,
    "NDTV": 2,
}


def rank_articles(articles):
    def score(a):
        coverage = a.get("coverageCount", 1)
        source = a.get("source", "")
        weight = CREDIBILITY_WEIGHTS.get(source, 1)

        # simple scoring formula
        return (coverage * 10) + (weight * 2)

    return sorted(articles, key=score, reverse=True)

import re

CATEGORY_KEYWORDS = {
    "Tech": [
        "ai", "artificial intelligence", "openai", "google", "microsoft",
        "apple", "iphone", "android", "startup", "tech", "software",
        "chip", "nvidia", "tesla", "cloud", "aws", "cyber", "hacker",
        "data breach", "security", "ransomware"
    ],
    "Business": [
        "stock", "stocks", "market", "inflation", "interest rate", "gdp",
        "rbi", "fed", "earnings", "revenue", "profit", "loss", "bank",
        "ipo", "share", "economy"
    ],
    "World": [
        "war", "ukraine", "russia", "china", "israel", "gaza",
        "united nations", "nato", "election", "president", "government",
        "parliament", "diplomatic"
    ],
    "Sports": [
        "cricket", "football", "fifa", "ipl", "world cup", "match",
        "tournament", "goal", "coach", "player", "team"
    ],
    "Security": [
        "breach", "cyber", "hacked", "ransomware", "attack",
        "malware", "phishing", "leak", "vulnerability"
    ],
}

def classify_category(article: dict) -> str:
    """
    Rule-based category classifier.
    Always returns one category.
    """
    text = f"{article.get('title','')} {article.get('summary','')}".lower()

    # Clean up text a bit
    text = re.sub(r"\s+", " ", text)

    scores = {}

    for category, keywords in CATEGORY_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text:
                score += 1
        scores[category] = score

    # pick best score
    best = max(scores, key=scores.get)

    # if no matches at all, fallback
    if scores[best] == 0:
        return "World"

    return best
