from newspaper import Article


def extract_article_text(url: str) -> str:
    """
    Downloads a news article and extracts the main readable text.
    """
    try:
        a = Article(url)
        a.download()
        a.parse()

        return (a.text or "").strip()

    except Exception:
        return ""
