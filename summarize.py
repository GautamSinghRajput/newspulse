"""
summarize.py
Uses the Gemini API for the tasks that genuinely need language understanding:
- naming + summarizing every cluster in ONE batched call (not one call per cluster)
- detecting framing/bias differences between sources covering the same story

Requires GEMINI_API_KEY to be set in the environment (.env file supported).
Get a key at https://aistudio.google.com/apikey
"""

import os
import json
import re
import time
from typing import List, Dict
from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv()

_client = None
MODEL = "gemini-3.1-flash-lite"

# --- Rate limiting -----------------------------------------------------
# Free-tier Gemini keys are commonly capped at a low RPM (e.g. 10-15).
# MIN_INTERVAL enforces a floor between any two calls regardless of how
# many clusters/features trigger them. Tune this up if you still hit 429s,
# or down if you're on a higher-tier key.
MIN_INTERVAL_SECONDS = 4.5
_last_call_ts = 0.0


def _get_client():
    global _client
    if _client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. Add it to a .env file or your environment."
            )
        _client = genai.Client(api_key=api_key)
    return _client


def _throttle():
    global _last_call_ts
    elapsed = time.monotonic() - _last_call_ts
    if elapsed < MIN_INTERVAL_SECONDS:
        time.sleep(MIN_INTERVAL_SECONDS - elapsed)
    _last_call_ts = time.monotonic()


def _call(prompt: str, max_tokens: int = 500, max_retries: int = 4) -> str:
    client = _get_client()
    for attempt in range(max_retries):
        _throttle()
        try:
            resp = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config={"max_output_tokens": max_tokens},
            )
            return (resp.text or "").strip()
        except genai_errors.ClientError as e:
            # 429 = rate limited. Back off and retry rather than failing the run.
            if "429" in str(e) or getattr(e, "code", None) == 429:
                wait = MIN_INTERVAL_SECONDS * (2 ** attempt)
                time.sleep(wait)
                continue
            raise
    raise RuntimeError("Gemini API rate limit exceeded after multiple retries. "
                       "Try again in a minute, or reduce the number of articles/clusters.")


def _extract_json(text: str):
    """Gemini sometimes wraps JSON in ```json fences — strip those before parsing."""
    cleaned = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    return json.loads(cleaned)


def expand_query(topic: str, max_terms: int = 6) -> List[str]:
    """
    Takes a free-text/personalized query (e.g. "indian army") and asks
    Gemini for closely related search terms so RSS keyword-matching and the
    Google News search both get better recall than plain substring matching
    on the literal phrase alone.
    """
    if not topic or not topic.strip():
        return []

    prompt = (
        f'A user wants news about: "{topic.strip()}"\n\n'
        f"Give up to {max_terms} closely related search terms/phrases that "
        "would help find ALL relevant news coverage on this topic (include "
        "official names, common abbreviations, related organizations/people, "
        "and near-synonyms). Respond with ONLY a JSON array of strings, no "
        'markdown fences, no preamble, e.g. ["term one", "term two"]'
    )
    try:
        raw = _call(prompt, max_tokens=150)
        terms = _extract_json(raw)
        if isinstance(terms, list):
            return [str(t).strip() for t in terms if str(t).strip()][:max_terms]
    except Exception:
        pass
    return []


def compare_framing(articles) -> str:
    """
    Given several articles covering the SAME story from different sources,
    identify differences in emphasis, word choice, or omitted facts.
    This is called on-demand (one theme at a time), so it stays a single call.
    """
    if len(articles) < 2:
        return "Not enough distinct sources on this story to compare framing."

    joined = "\n\n".join(
        f"SOURCE: {a.source}\nTITLE: {a.title}\nEXCERPT: {a.text[:600]}"
        for a in articles[:4]
    )
    prompt = (
        "The following are excerpts from different news outlets covering the "
        "same story. Identify concrete differences in how they frame it: "
        "differences in emphasis, word choice/tone, or facts one source "
        "includes that another omits. Be specific and cite the source names. "
        "Keep it to 4-5 sentences.\n\n"
        f"{joined}"
    )
    return _call(prompt, max_tokens=350)


def build_report(clusters: Dict[int, list]) -> List[dict]:
    """
    Names + summarizes ALL clusters in a single Gemini call (not one call per
    cluster) to keep requests-per-minute low. Falls back to a simple
    per-cluster loop only if the batched JSON response fails to parse.
    """
    cluster_items = list(clusters.items())

    blocks = []
    for cid, articles in cluster_items:
        headlines = "; ".join(a.title for a in articles[:6])
        excerpt = " ".join(a.text[:300] for a in articles[:3])
        blocks.append(f'CLUSTER_ID: {cid}\nHEADLINES: {headlines}\nEXCERPT: {excerpt[:800]}')

    joined = "\n\n".join(blocks)
    prompt = (
        "You will be given several clusters of related news articles. For EACH "
        "cluster, produce a short theme name (3-6 words) and a 2-3 sentence "
        "summary of the collective coverage (what happened and why it matters).\n\n"
        "Respond with ONLY a JSON array, no markdown fences, no preamble, in this "
        'exact shape: [{"cluster_id": <int>, "theme": "<name>", "summary": "<summary>"}, ...]\n\n'
        f"{joined}"
    )

    raw = _call(prompt, max_tokens=200 * max(1, len(cluster_items)))

    try:
        parsed = _extract_json(raw)
        by_id = {int(item["cluster_id"]): item for item in parsed}
    except Exception:
        by_id = {}

    report = []
    for cid, articles in cluster_items:
        item = by_id.get(cid)
        report.append(
            {
                "cluster_id": cid,
                "theme": item["theme"] if item else f"Theme {cid}",
                "summary": item["summary"] if item else "Summary unavailable (parse fallback).",
                "article_count": len(articles),
                "sources": sorted(set(a.source for a in articles)),
            }
        )
    return report