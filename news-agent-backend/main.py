from services.newsapi_service import fetch_from_newsapi
from services.rss_service import fetch_from_rss

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from typing import List

from services.scrape_service import extract_article_text

from services.processing_service import (
    filter_by_date_range,
    deduplicate_articles,
    rank_articles,
    classify_category,
)

from services.gemini_service import (
    summarize_article,
    summarize_article_deep,
    summarize_executive,
)


# -----------------------------
# Request Models
# -----------------------------
class RunAgentRequest(BaseModel):
    fromDate: str
    toDate: str
    sources: List[str]


class ArticleSummaryRequest(BaseModel):
    title: str
    snippet: str


class UrlSummaryRequest(BaseModel):
    title: str
    url: str


# -----------------------------
# FastAPI App
# -----------------------------
app = FastAPI(title="News Intelligence Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # later we will lock this down
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Routes
# -----------------------------
@app.get("/")
def health():
    return {"status": "ok", "message": "Backend is running"}


@app.post("/agent/run")
def run_agent(payload: RunAgentRequest):
    # -----------------------------
    # 1) Fetch articles (ONLY selected sources)
    # -----------------------------

    # NewsAPI (only if user selected "reuters")
    newsapi_articles = []
    if "reuters" in payload.sources:
        newsapi_articles = fetch_from_newsapi(payload.fromDate, payload.toDate)

    # RSS (only selected RSS sources)
    rss_articles = fetch_from_rss(payload.sources)

    all_articles = newsapi_articles + rss_articles

    # -----------------------------
    # 2) Filter, dedupe, rank
    # -----------------------------
    all_articles = filter_by_date_range(all_articles, payload.fromDate, payload.toDate)
    all_articles = deduplicate_articles(all_articles)
    all_articles = rank_articles(all_articles)

    # -----------------------------
    # 3) Add category field (for UI tabs + filters)
    # -----------------------------
    for a in all_articles:
        a["category"] = classify_category(a)

    # -----------------------------
    # 4) Generate short summaries (top 10 only)
    # -----------------------------
    TOP_N_FOR_SUMMARY = 10

    for i in range(min(TOP_N_FOR_SUMMARY, len(all_articles))):
        a = all_articles[i]

        # IMPORTANT: use real text fields
        text = (
            a.get("content")
            or a.get("description")
            or a.get("summary")
            or a.get("snippet")
            or ""
        )

        # Save raw text (for debugging + deep summary fallback)
        a["raw_text"] = text

        # Short summary (2-3 lines)
        a["summary"] = summarize_article(a.get("title", ""), text)

    # -----------------------------
    # 5) Executive summary (only top 10 ranked)
    # -----------------------------
    executive_summary = summarize_executive(all_articles[:10])

    return {
        "executive_summary": executive_summary,
        "articles": all_articles[:40],
    }


@app.post("/agent/article-summary")
def article_summary(payload: ArticleSummaryRequest):
    """
    Old endpoint: deep summary from snippet sent by frontend.
    """
    deep = summarize_article_deep(payload.title, payload.snippet)

    if deep:
        return {"deep_summary": deep}

    return {"deep_summary": payload.snippet[:300]}


@app.post("/agent/deep-summary-url")
def deep_summary_url(payload: UrlSummaryRequest):
    """
    Best endpoint:
    Extracts full article text from URL and summarizes it.
    """
    text = extract_article_text(payload.url)

    if not text or len(text.strip()) < 80:
        return {"deep_summary": "Could not extract enough text from this website."}

    deep = summarize_article_deep(payload.title, text)
    return {"deep_summary": deep}
