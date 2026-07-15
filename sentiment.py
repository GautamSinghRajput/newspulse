"""
sentiment.py
Runs local sentiment scoring with FinBERT — trained on financial/news text
(analyst reports, earnings calls, news headlines), unlike generic sentiment
models trained on movie/product reviews. "Layoffs planned" and "stock
surges" read very differently to a model that actually knows financial
and news language. No API key needed.
"""

from typing import List, Dict
from collections import defaultdict
from datetime import datetime

_pipe = None


def _get_pipeline():
    global _pipe
    if _pipe is None:
        from transformers import pipeline
        _pipe = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            truncation=True,
        )
    return _pipe


def _all_class_scores(pipe, text: str) -> Dict[str, float]:
    """
    Returns {"positive": p, "negative": p, "neutral": p} regardless of the
    installed transformers version's kwarg name for "give me all classes".
    """
    try:
        result = pipe(text, top_k=None)  # newer transformers
    except TypeError:
        result = pipe(text, return_all_scores=True)  # older transformers
    # Single input can come back as a flat list of dicts, or a list-of-list.
    if result and isinstance(result[0], list):
        result = result[0]
    return {r["label"].lower(): r["score"] for r in result}


def score_articles(articles) -> None:
    """
    Attaches `.sentiment_label` and `.sentiment_score` (-1..1) to each
    article in place. Score is P(positive) - P(negative), so a confident
    neutral reads as ~0 while a mixed positive/negative story still gets a
    meaningful signed score rather than collapsing to a single top label.
    """
    pipe = _get_pipeline()
    for art in articles:
        text = (art.title + ". " + art.text)[:512]
        try:
            scores = _all_class_scores(pipe, text)
            pos = scores.get("positive", 0.0)
            neg = scores.get("negative", 0.0)
            art.sentiment_score = pos - neg
            art.sentiment_label = max(scores, key=scores.get).upper()
        except Exception:
            art.sentiment_label = "NEUTRAL"
            art.sentiment_score = 0.0


def cluster_sentiment(clusters: Dict[int, list]) -> Dict[int, float]:
    """Average sentiment score per cluster."""
    return {
        cid: sum(getattr(a, "sentiment_score", 0.0) for a in arts) / len(arts)
        for cid, arts in clusters.items()
    }


def sentiment_trend(articles) -> List[dict]:
    """
    Buckets articles by day and returns average sentiment per day,
    used to plot a trend line over the coverage window.
    """
    by_day = defaultdict(list)
    for art in articles:
        try:
            day = datetime.fromisoformat(art.published).date().isoformat()
        except ValueError:
            day = "unknown"
        by_day[day].append(getattr(art, "sentiment_score", 0.0))

    trend = [
        {"date": day, "avg_sentiment": sum(scores) / len(scores), "count": len(scores)}
        for day, scores in sorted(by_day.items())
        if day != "unknown"
    ]
    return trend


def source_sentiment(articles, min_articles: int = 1) -> List[dict]:
    """
    Average sentiment per outlet across the whole fetched batch — this is
    the comparison that actually surfaces something useful: which specific
    sources are framing this topic more positively or negatively than
    others, rather than one abstract number with nothing to compare it to.
    Sources with fewer than `min_articles` are dropped (a single article's
    score isn't a meaningful "outlet lean").
    """
    by_source = defaultdict(list)
    for art in articles:
        by_source[art.source].append(getattr(art, "sentiment_score", 0.0))

    results = [
        {"source": src, "avg_sentiment": sum(scores) / len(scores), "count": len(scores)}
        for src, scores in by_source.items()
        if len(scores) >= min_articles
    ]
    results.sort(key=lambda r: r["avg_sentiment"])
    return results