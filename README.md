# NewsPulse: Topic Tracker and Summarizer

Tracks tech/AI and financial/business news, clusters it into themes, summarizes
each theme, tracks sentiment over time, and highlights how different outlets
frame the same story.

## What it does
- **Fetch**: Pulls recent articles from a curated list of tech/AI and
  financial/business RSS feeds (TechCrunch, The Verge, Reuters Business,
  Economic Times, LiveMint, MoneyControl, etc.) — no news API key required.
- **Cluster**: Embeds articles locally (`sentence-transformers`, CPU-only,
  no API key) and groups them into themes with KMeans, auto-picking the
  cluster count via silhouette score.
- **Summarize**: Uses Claude to name each theme and write a 2-3 sentence
  summary of the collective coverage.
- **Sentiment**: Scores each article locally (DistilBERT sentiment model,
  no API key) and aggregates it per theme and per day for a trend chart.
- **Bias / framing comparison**: For themes covered by 2+ sources, asks
  Claude to point out concrete differences in emphasis, tone, or omitted
  facts between outlets — the project's required differentiator.

## Setup

1. **Install dependencies** (Python 3.10+ recommended):
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Anthropic API key**:
   ```bash
   cp .env .env
   # then edit .env and paste your key
   ```
   Get a key at https://console.anthropic.com/

3. **Run the app**:
   ```bash
   streamlit run app.py
   ```

   First run will download the local embedding model (`all-MiniLM-L6-v2`,
   ~90MB) and sentiment model (~250MB) — this needs an internet connection
   once, then they're cached locally.

## Usage
1. Enter topic keywords in the sidebar (e.g. `AI, funding` or `RBI, interest
   rate`), or leave blank to pull top stories from all selected sources.
2. Adjust the look-back window and source list as needed.
3. Click **Fetch & Analyze**.
4. Explore the three tabs:
   - **Themes** — clustered stories with summaries and sentiment
   - **Sentiment Trend** — sentiment over time as a line chart
   - **Bias / Framing Comparison** — pick a multi-source theme and see how
     coverage differs across outlets

## Project structure
```
newspulse/
├── app.py            # Streamlit UI
├── fetch_news.py      # RSS ingestion (feedparser + optional full-text via newspaper3k)
├── cluster.py         # Local embeddings + KMeans clustering
├── sentiment.py       # Local sentiment scoring + trend aggregation
├── summarize.py        # Claude-powered theme naming, summarization, bias comparison
├── requirements.txt
└── .env.example
```

## Notes on required project outcomes
1. **Summarize and theme-cluster a set of news articles, deployed** →
   `cluster.py` + `summarize.py` + Streamlit "Themes" tab.
2. **Report a defensible sentiment trend across the coverage** →
   `sentiment.py`'s `sentiment_trend()` + the "Sentiment Trend" tab,
   backed by a real sentiment classifier (not just an LLM guess), so the
   numbers are reproducible.
3. **Bias-spread detection contrasting how sources frame the same theme** →
   `compare_framing()` in `summarize.py` + the "Bias / Framing Comparison" tab.

## Deploying
Push this folder to a GitHub repo and deploy on
[Streamlit Community Cloud](https://streamlit.io/cloud):
- Set `ANTHROPIC_API_KEY` as a secret in the app settings (not committed to
  the repo).
- Point the app entry point to `app.py`.

## Known limitations to mention in your report
- RSS feeds sometimes throttle or block automated requests (HTTP 403) —
  the app degrades gracefully by skipping that feed rather than crashing.
- Full-text download (`newspaper3k`) can fail on paywalled sites; the app
  falls back to the RSS summary text automatically.
- Clustering quality depends on article volume — very narrow keyword
  searches with few results will yield 1 broad cluster rather than several.
