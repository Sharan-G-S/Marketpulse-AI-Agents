"""
News Digest Formatter for MarketPulse.

Aggregates raw news articles for a ticker into a structured daily digest:
  - deduplication by title similarity
  - sentiment-weighted relevance ranking
  - Markdown digest builder
  - Plain-text snippet for report embedding

No LLM calls — pure string processing and heuristics.
"""

from datetime import datetime, timezone
import re
from typing import Any, Dict, List, Optional

# ── Type aliases ──────────────────────────────────────────────────────────────

Article = Dict[str, Any]
"""
{
    "title":       str,
    "description": str | None,
    "url":         str | None,
    "publishedAt": str | None,   # ISO-8601 or YYYY-MM-DD
    "source":      str | None,
    "sentiment":   str | None,   # "Bullish" | "Bearish" | "Neutral"
    "score":       float | None, # -1.0 to +1.0
}
"""

DigestEntry = Dict[str, Any]
"""
{
    "title":     str,
    "source":    str,
    "date":      str,            # YYYY-MM-DD
    "url":       str,
    "sentiment": str,
    "score":     float,
    "snippet":   str,            # first 160 chars of description
}
"""


# ── Deduplication ─────────────────────────────────────────────────────────────

def _normalise(text: str) -> str:
    """Lowercase, strip punctuation, collapse whitespace."""
    text = text.lower()
    text = re.sub(r"[^\w\s]", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _jaccard(a: str, b: str) -> float:
    """Token-level Jaccard similarity between two strings."""
    sa, sb = set(_normalise(a).split()), set(_normalise(b).split())
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def deduplicate_articles(
    articles: List[Article],
    threshold: float = 0.6,
) -> List[Article]:
    """
    Remove near-duplicate articles based on title Jaccard similarity.

    Args:
        articles:  List of Article dicts, ordered by relevance/date.
        threshold: Similarity threshold above which an article is considered
                   a duplicate (default 0.6 = 60 % token overlap).

    Returns:
        Deduplicated list preserving original order.
    """
    seen_titles: List[str] = []
    unique: List[Article] = []
    for art in articles:
        title = art.get("title", "")
        if not any(_jaccard(title, s) >= threshold for s in seen_titles):
            seen_titles.append(title)
            unique.append(art)
    return unique


# ── Ranking ───────────────────────────────────────────────────────────────────

def _sentiment_weight(article: Article) -> float:
    """Higher absolute score = more informative for ranking."""
    score = article.get("score")
    if score is not None:
        try:
            return abs(float(score))
        except (ValueError, TypeError):
            pass
    label = article.get("sentiment", "Neutral")
    return {"Bullish": 0.7, "Bearish": 0.7, "Neutral": 0.3}.get(label, 0.3)


def rank_articles(articles: List[Article], top_n: int = 10) -> List[Article]:
    """
    Rank articles by |sentiment_score| descending and return top-N.
    Articles with no score are ranked last.
    """
    ranked = sorted(articles, key=_sentiment_weight, reverse=True)
    return ranked[:top_n]


# ── Digest building ───────────────────────────────────────────────────────────

_SENTIMENT_EMOJI = {"Bullish": "🟢", "Bearish": "🔴", "Neutral": "⚪"}


def _parse_date(raw: Optional[str]) -> str:
    """Return YYYY-MM-DD or 'Unknown'."""
    if not raw:
        return "Unknown"
    try:
        return raw[:10]
    except Exception:
        return "Unknown"


def build_digest_entries(articles: List[Article]) -> List[DigestEntry]:
    """Convert raw Article dicts into structured DigestEntry dicts."""
    entries: List[DigestEntry] = []
    for art in articles:
        sentiment = art.get("sentiment") or "Neutral"
        score     = art.get("score")
        try:
            score = float(score) if score is not None else 0.0
        except (ValueError, TypeError):
            score = 0.0

        desc    = art.get("description") or ""
        snippet = (desc[:160] + "…") if len(desc) > 160 else desc

        entries.append({
            "title":     art.get("title", "Untitled"),
            "source":    art.get("source", "Unknown"),
            "date":      _parse_date(art.get("publishedAt") or art.get("date")),
            "url":       art.get("url", ""),
            "sentiment": sentiment,
            "score":     round(score, 3),
            "snippet":   snippet,
        })
    return entries


def format_news_digest_markdown(
    ticker: str,
    entries: List[DigestEntry],
    max_articles: int = 8,
) -> str:
    """
    Render a Markdown news digest for a ticker.

    Args:
        ticker:       Stock symbol.
        entries:      List of DigestEntry dicts (already ranked/deduped).
        max_articles: Maximum articles to include.

    Returns:
        Multi-line Markdown string.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        f"## 📰 News Digest — {ticker.upper()}",
        f"*Generated {now} · {len(entries[:max_articles])} article(s)*",
        "",
    ]

    if not entries:
        lines.append("_No news articles found for this ticker._")
        return "\n".join(lines)

    for i, e in enumerate(entries[:max_articles], 1):
        emoji = _SENTIMENT_EMOJI.get(e["sentiment"], "⚪")
        title = e["title"]
        url   = e.get("url", "")
        link  = f"[{title}]({url})" if url else title

        lines.append(f"### {i}. {emoji} {link}")
        lines.append(
            f"**{e['source']}** · {e['date']} · "
            f"Sentiment: {e['sentiment']} (score: {e['score']:+.2f})"
        )
        if e["snippet"]:
            lines.append(f"> {e['snippet']}")
        lines.append("")

    return "\n".join(lines)


def digest_sentiment_summary(entries: List[DigestEntry]) -> Dict[str, Any]:
    """
    Compute aggregate sentiment stats from a list of DigestEntry dicts.

    Returns:
        Dict with bullish_count, bearish_count, neutral_count,
        avg_score, dominant_sentiment.
    """
    counts = {"Bullish": 0, "Bearish": 0, "Neutral": 0}
    scores = []
    for e in entries:
        label = e.get("sentiment", "Neutral")
        counts[label] = counts.get(label, 0) + 1
        scores.append(e.get("score", 0.0))

    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0
    dominant  = max(counts, key=counts.get)  # type: ignore[arg-type]

    return {
        "bullish_count":    counts.get("Bullish", 0),
        "bearish_count":    counts.get("Bearish", 0),
        "neutral_count":    counts.get("Neutral", 0),
        "avg_score":        avg_score,
        "dominant_sentiment": dominant,
        "total":            len(entries),
    }
