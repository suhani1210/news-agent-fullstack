import feedparser
import re

RSS_FEEDS = [
    # General
    ("bbc", "BBC", "http://feeds.bbci.co.uk/news/rss.xml"),
    ("reuters_rss", "Reuters (RSS)", "https://feeds.reuters.com/reuters/topNews"),

    # Tech
    ("techcrunch", "TechCrunch", "https://techcrunch.com/feed/"),
    ("theverge", "The Verge", "https://www.theverge.com/rss/index.xml"),
    ("arstechnica", "Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("wired", "Wired", "https://www.wired.com/feed/rss"),
    ("mittechreview", "MIT Technology Review", "https://www.technologyreview.com/feed/"),
    ("venturebeat", "VentureBeat", "https://venturebeat.com/feed/"),
    ("theregister", "The Register", "https://www.theregister.com/headlines.atom"),

    # Hacker News
    ("hackernews", "Hacker News", "https://hnrss.org/frontpage"),
]
def clean_html(text: str) -> str:
    if not text:
        return ""

    # remove HTML tags
    text = re.sub(r"<[^>]+>", " ", text)

    # remove extra whitespace
    text = re.sub(r"\s+", " ", text).strip()

    return text


def fetch_from_rss(selected_source_ids=None):
    """
    selected_source_ids: list of ids from frontend
    Example: ["bbc", "techcrunch", "wired"]
    """
    if selected_source_ids is None:
        selected_source_ids = []

    # If user didn't select anything, return nothing
    if len(selected_source_ids) == 0:
        return []

    articles = []

    for feed_id, source_name, feed_url in RSS_FEEDS:
        # Skip feeds not selected
        if feed_id not in selected_source_ids:
            continue

        try:
            feed = feedparser.parse(feed_url)

            for entry in feed.entries[:25]:
                published = ""
                if hasattr(entry, "published"):
                    published = entry.published

                snippet = entry.get("summary", "") or entry.get("description", "")
                snippet = clean_html(snippet)
                snippet = snippet[:400]

                articles.append(
                    {
                        "id": entry.get("link") or entry.get("id") or "",
                        "title": entry.get("title") or "",
                        "source": source_name,
                        "publishedAt": published,
                        "tags": [],
                        "summary": snippet,
                        "description": snippet,
                        "content": snippet,
                        "url": entry.get("link") or "",
                        "coverageCount": 1,
                        "isDuplicateGroup": False,
                    }
                )

        except Exception:
            continue

    return articles
