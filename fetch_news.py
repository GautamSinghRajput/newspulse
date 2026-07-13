"""
fetch_news.py
Pulls recent articles for a chosen topic from either a curated set of
tech/AI and financial/business RSS feeds, or an open-ended Google News
search (any topic, not limited to the curated list). No API key required
for either path.
"""

import feedparser
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from typing import List
from urllib.parse import quote
import time

# Curated feeds across tech/AI and financial/business sources.
# Each feed is tagged with a source name used later for bias-comparison.
FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "The Verge": "https://www.theverge.com/rss/index.xml",
    "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
    "Wired": "https://www.wired.com/feed/rss",
    "Reuters Business": "https://feeds.reuters.com/reuters/businessNews",
    "Economic Times": "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    "LiveMint": "https://www.livemint.com/rss/news",
    "MoneyControl": "https://www.moneycontrol.com/rss/latestnews.xml",
    "CNBC Tech": "https://www.cnbc.com/id/19854910/device/rss/rss.html",
}

GOOGLE_NEWS_SEARCH_URL = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
GOOGLE_NEWS_TOPIC_URL = "https://news.google.com/rss/headlines/section/topic/{topic}?hl=en-IN&gl=IN&ceid=IN:en"


@dataclass
class Article:
    title: str
    link: str
    source: str
    published: str
    summary: str
    body: str = field(default="")
    image: str = field(default="")

    @property
    def text(self) -> str:
        """Best available text for embedding/summarization."""
        return self.body if len(self.body) > len(self.summary) else self.summary


def _matches_topic(entry, keywords: List[str]) -> bool:
    if not keywords:
        return True
    haystack = (entry.get("title", "") + " " + entry.get("summary", "")).lower()
    return any(kw.lower().strip() in haystack for kw in keywords)


def _parse_published(entry) -> str:
    for key in ("published_parsed", "updated_parsed"):
        val = entry.get(key)
        if val:
            return datetime.fromtimestamp(time.mktime(val)).isoformat()
    return datetime.now().isoformat()


def fetch_articles(
        topic: str,
        max_articles: int = 40,
        days_back: int = 7,
        sources: List[str] = None,
        extra_keywords: List[str] = None,
) -> List[Article]:
    """
    Fetch articles matching `topic` (comma-separated keywords are supported,
    e.g. "AI, funding, layoffs") from the curated RSS feed list.

    `extra_keywords` (e.g. from Gemini query expansion) are OR'd in with the
    topic keywords to widen recall — an article matching any one of them
    (topic OR expansion term) is included.
    """
    keywords = [k for k in topic.split(",") if k.strip()] if topic else []
    keywords += [k for k in (extra_keywords or []) if k.strip()]
    cutoff = datetime.now() - timedelta(days=days_back)
    chosen_feeds = {k: v for k, v in FEEDS.items() if not sources or k in sources}

    articles: List[Article] = []
    for source_name, feed_url in chosen_feeds.items():
        try:
            parsed = feedparser.parse(feed_url)
        except Exception:
            continue

        for entry in parsed.entries:
            if not _matches_topic(entry, keywords):
                continue

            published = _parse_published(entry)
            try:
                if datetime.fromisoformat(published) < cutoff:
                    continue
            except ValueError:
                pass

            articles.append(
                Article(
                    title=entry.get("title", "Untitled"),
                    link=entry.get("link", ""),
                    source=source_name,
                    published=published,
                    summary=entry.get("summary", "")[:2000],
                )
            )

    articles.sort(key=lambda a: a.published, reverse=True)
    return articles[:max_articles]


def fetch_google_news(
        query: str,
        max_articles: int = 30,
        days_back: int = 7,
) -> List[Article]:
    """
    Open-ended search across Google News' aggregated index — not limited to
    the curated FEEDS list, so any topic (e.g. "Indian Army", "RBI repo
    rate", "K-pop industry") returns real matching coverage from whichever
    outlets Google has indexed for it. No API key required.
    """
    if not query or not query.strip():
        return []

    url = GOOGLE_NEWS_SEARCH_URL.format(query=quote(query.strip()))
    try:
        parsed = feedparser.parse(url)
    except Exception:
        return []

    cutoff = datetime.now() - timedelta(days=days_back)
    articles: List[Article] = []

    for entry in parsed.entries:
        published = _parse_published(entry)
        try:
            if datetime.fromisoformat(published) < cutoff:
                continue
        except ValueError:
            pass

        # Google News RSS tags each entry with a <source> element for the
        # original publisher (e.g. "The Times of India").
        source_name = "Google News"
        src = entry.get("source")
        if src and getattr(src, "title", None):
            source_name = src.title
        elif isinstance(src, dict) and src.get("title"):
            source_name = src["title"]

        articles.append(
            Article(
                title=entry.get("title", "Untitled"),
                link=entry.get("link", ""),
                source=source_name,
                published=published,
                summary=entry.get("summary", "")[:2000],
            )
        )

    articles.sort(key=lambda a: a.published, reverse=True)
    return articles[:max_articles]


def fetch_trending_headlines(max_articles: int = 8, days_back: int = 2) -> List[Article]:
    """
    Pulls top current headlines from Google News' Technology and Business
    topic feeds — matching NewsPulse's registered domain — for a homepage
    preview shown before the user runs any search.
    """
    articles: List[Article] = []
    for topic in ("TECHNOLOGY", "BUSINESS"):
        url = GOOGLE_NEWS_TOPIC_URL.format(topic=topic)
        try:
            parsed = feedparser.parse(url)
        except Exception:
            continue

        for entry in parsed.entries[:max_articles]:
            published = _parse_published(entry)
            source_name = "Google News"
            src = entry.get("source")
            if src and getattr(src, "title", None):
                source_name = src.title
            elif isinstance(src, dict) and src.get("title"):
                source_name = src["title"]

            articles.append(
                Article(
                    title=entry.get("title", "Untitled"),
                    link=entry.get("link", ""),
                    source=source_name,
                    published=published,
                    summary=entry.get("summary", "")[:2000],
                )
            )

    cutoff = datetime.now() - timedelta(days=days_back)
    fresh = []
    for a in articles:
        try:
            if datetime.fromisoformat(a.published) >= cutoff:
                fresh.append(a)
        except ValueError:
            fresh.append(a)

    fresh.sort(key=lambda a: a.published, reverse=True)
    return fresh[:max_articles]


def merge_and_dedupe(*article_lists: List[Article], max_articles: int = 60) -> List[Article]:
    """Combines multiple article lists, deduping by normalized title."""
    seen = set()
    merged: List[Article] = []
    for lst in article_lists:
        for art in lst:
            key = art.title.strip().lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(art)
    merged.sort(key=lambda a: a.published, reverse=True)
    return merged[:max_articles]


def _resolve_real_url(url: str, timeout: float = 6.0) -> str:
    """
    Google News RSS links no longer use a simple HTTP redirect — they're an
    opaque encoded ID (news.google.com/rss/articles/CBMi...) that requires
    decoding via Google's internal batchexecute endpoint to recover the real
    publisher URL. Without this, scraping the link directly just grabs
    Google News' own page (and its logo) instead of the actual article.
    """
    if "news.google.com" not in url:
        return url
    try:
        from googlenewsdecoder import new_decoderv1
        result = new_decoderv1(url, interval=1)
        if result.get("status") and result.get("decoded_url"):
            return result["decoded_url"]
    except Exception:
        pass
    return url


def enrich_with_full_text(articles: List[Article], max_articles: int = 25) -> List[Article]:
    """
    Optionally download full article bodies for better clustering/summaries,
    and capture each article's main image along the way (newspaper3k
    extracts both in the same download/parse call, so the image is
    effectively free once we're already fetching the page for its text).
    Google News links are resolved to the real publisher URL first, so we
    scrape the actual article page rather than Google's redirect page.
    Falls back silently if download/resolution fails (paywalls, blocked
    scraping, JS-only redirects, etc.) — no image is shown rather than a
    wrong one.
    """
    try:
        from newspaper import Article as NPArticle, Config
    except ImportError:
        return articles

    # Many publisher sites block newspaper3k's default User-Agent outright.
    # A real browser UA noticeably improves scrape success rate.
    config = Config()
    config.browser_user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    )
    config.request_timeout = 10

    for art in articles[:max_articles]:
        try:
            real_url = _resolve_real_url(art.link)
            if "news.google.com" in real_url:
                continue  # couldn't resolve to the real publisher page — skip rather than mis-scrape
            np_art = NPArticle(real_url, config=config)
            np_art.download()
            np_art.parse()
            if np_art.text and len(np_art.text) > len(art.summary):
                art.body = np_art.text[:5000]
            if np_art.top_image:
                art.image = np_art.top_image
        except Exception:
            continue

    return articles