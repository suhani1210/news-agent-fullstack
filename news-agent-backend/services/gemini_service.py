import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


def gemini_available():
    return bool(GEMINI_API_KEY)


def init_gemini():
    genai.configure(api_key=GEMINI_API_KEY)


def summarize_article(title: str, snippet: str):
    """
    Returns 2-3 sentence summary for one article.
    """
    if not GEMINI_API_KEY:
        return snippet[:220] if snippet else ""

    try:
        init_gemini()
        model = genai.GenerativeModel("gemini-1.5-flash")

        prompt = f"""
You are a news summarizer for a corporate dashboard.

Task:
Write EXACTLY 2 to 3 short sentences in very simple English.

Article:
Title: {title}
Text: {snippet}

Rules:
- Must be 2 or 3 sentences only
- No bullet points
- No emojis
- No opinions
- No extra headings
- Mention what happened and why it matters
"""

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.3,
                "max_output_tokens": 120,
            },
        )

        return (res.text or "").strip()

    except Exception:
        return snippet[:220] if snippet else ""


def summarize_executive(articles):
    """
    Returns executive summary for the whole run (6-8 bullet points).
    """
    if not GEMINI_API_KEY:
        return "Summary unavailable (Gemini key missing)."

    try:
        init_gemini()
        model = genai.GenerativeModel("gemini-1.5-flash")

        titles = "\n".join([f"- {a.get('title','')}" for a in articles[:14]])

        prompt = f"""
You are writing an executive news digest for senior leadership.

Input (headlines only):
{titles}

Task:
Write 6 to 8 bullet points that summarize the major themes.

Rules:
- Bullet points only
- Each bullet should be ONE line
- Simple business language
- No speculation, no opinions
- Do not repeat the same topic twice
- Cover: world, business, tech, security if present
"""

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.35,
                "max_output_tokens": 220,
            },
        )

        return (res.text or "").strip()

    except Exception:
        return "Summary unavailable (Gemini failed)."


def summarize_article_deep(title: str, snippet: str):
    """
    Returns a longer paragraph summary (deep summary).
    """
    if not GEMINI_API_KEY:
        return snippet[:550] if snippet else "Gemini key missing."

    # If snippet is too short, Gemini will output short (and should)
    # so we ensure it has at least something
    if not snippet or len(snippet.strip()) < 40:
        return "Not enough article text available to generate a deep summary."

    try:
        init_gemini()

        # IMPORTANT: Use PRO for deep summary
        model = genai.GenerativeModel("gemini-1.5-pro")

        prompt = f"""
You are a Senior Business Intelligence Analyst at a multinational company.
Write an executive briefing for a corporate dashboard.

Article:
Title: {title}
Text: {snippet}

TASK:
Write EXACTLY ONE cohesive paragraph.
Target length: 110 to 160 words (strict).

STRUCTURE (must be followed in the paragraph):
1) Lead: Start directly with what happened (core event).
2) Context: Mention who is involved (company/person/country).
3) Facts: Include at least TWO specific facts such as numbers, dates, amounts, or counts IF present in the text.
4) Impact: Explain why it matters (business, markets, security, policy, or society).
5) Outlook: End with what could happen next ONLY if the text clearly mentions it.

STRICT RULES:
- One paragraph only (no bullet points, no headings).
- Simple, newsroom-style English (direct and professional).
- Neutral tone: no opinions, no exaggeration, no assumptions.
- Do not write: "this article says" / "the author says".
- Make it flow naturally like a real briefing, not a list.
- Must be at least 6 sentences.
"""

        res = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.4,
                "max_output_tokens": 250,
            },
        )

        return (res.text or "").strip()

    except Exception:
        return snippet[:550] if snippet else ""
