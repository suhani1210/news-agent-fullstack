import os
import requests
from dotenv import load_dotenv

load_dotenv()

NEWSAPI_KEY = os.getenv("NEWSAPI_KEY")


def fetch_from_newsapi(from_date: str, to_date: str, query: str = None):
    if not NEWSAPI_KEY:
        return []

    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query or "news",
        "from": from_date[:10],
        "to": to_date[:10],
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 50,
        "apiKey": NEWSAPI_KEY,
    }

    try:
        res = requests.get(url, params=params, timeout=20)
        data = res.json()

        if data.get("status") != "ok":
            return []

        articles = []
        for a in data.get("articles", []):
            articles.append(
                {
                    "id": a.get("url"),
                    "title": a.get("title") or "",
                    "source": (a.get("source") or {}).get("name") or "NewsAPI",
                    "publishedAt": a.get("publishedAt") or "",
                    "tags": [],
                    "summary": a.get("description") or "",
                    "url": a.get("url") or "",
                    "coverageCount": 1,
                    "isDuplicateGroup": False,
                }
            )

        return articles

    except Exception:
        return []
