"""
NewsPulse: Topic Tracker and Summarizer
Streamlit app entry point.
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from fetch_news import (
    fetch_articles, fetch_google_news, fetch_trending_headlines,
    merge_and_dedupe, enrich_with_full_text, FEEDS,
)
from cluster import embed_articles, cluster_articles
from sentiment import score_articles, cluster_sentiment, sentiment_trend
from summarize import build_report, compare_framing, expand_query
import theme

st.set_page_config(page_title="NewsPulse", page_icon="🔴", layout="centered")
theme.inject_theme()

theme.render_hero(
    eyebrow="News Intelligence",
    title="NewsPulse",
    subtitle="Technology, AI, and financial news — clustered, summarized, "
             "and compared across sources in real time.",
)


@st.cache_data(ttl=1800, show_spinner=False)
def load_top_headlines():
    """
    Cached for 30 minutes so opening the page or tweaking a slider doesn't
    re-scrape thumbnail images on every rerun.
    """
    heads = fetch_trending_headlines(max_articles=8)
    heads = enrich_with_full_text(heads, max_articles=8)
    return heads


try:
    with st.spinner("Loading today's headlines..."):
        top_headlines = load_top_headlines()
    if top_headlines:
        st.markdown("##### Today's headlines")
        theme.render_headline_cards(top_headlines)
        st.markdown("<hr class='np-divider' />", unsafe_allow_html=True)
except Exception:
    pass  # Homepage preview is a nice-to-have; never block the app on it.

with st.container(border=True):
    st.markdown("##### Search settings")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        topic = st.text_input(
            "Search anything (e.g. 'Indian Army', 'AI funding', 'RBI repo rate')",
            value="AI, funding",
            help="Not limited to keywords in curated feeds — with Google News "
                 "search on, any topic works.",
        )
    with col2:
        days_back = st.slider("Look back (days)", 1, 14, 7)
    with col3:
        max_articles = st.slider("Max articles", 10, 60, 30)

    col4, col5 = st.columns(2)
    with col4:
        use_gemini_expansion = st.checkbox(
            "🧠 Personalize with Gemini",
            value=True,
            help="Expands your query into related terms (e.g. 'Indian Army' → "
                 "'Indian Armed Forces', 'Ministry of Defence India', ...) for "
                 "much better recall than exact keyword matching.",
        )
    with col5:
        use_google_news = st.checkbox(
            "🌐 Include Google News search",
            value=True,
            help="Searches across Google News' full index, not just the "
                 "curated feeds below — works for any topic.",
        )

    selected_sources = st.multiselect(
        "Curated feeds (in addition to Google News above)",
        options=list(FEEDS.keys()), default=list(FEEDS.keys())
    )
    fetch_full_text = st.checkbox("Download full article text (slower, better quality)", value=True)
    run = st.button("🔍 Fetch & Analyze", type="primary", use_container_width=True)

st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

if "report" not in st.session_state:
    st.session_state.report = None

if run:
    expanded_terms = []
    if use_gemini_expansion:
        with st.spinner("Personalizing search with Gemini..."):
            expanded_terms = expand_query(topic)

    with st.spinner("Fetching articles..."):
        curated = fetch_articles(
            topic,
            max_articles=max_articles,
            days_back=days_back,
            sources=selected_sources,
            extra_keywords=expanded_terms,
        )

        google_articles = []
        if use_google_news:
            # Search the original topic plus a couple of expansion terms so
            # the Google News query itself benefits from personalization too.
            search_query = topic if not expanded_terms else f"{topic} OR {expanded_terms[0]}"
            google_articles = fetch_google_news(
                search_query, max_articles=max_articles, days_back=days_back
            )

        articles = merge_and_dedupe(curated, google_articles, max_articles=max_articles)

    if expanded_terms:
        st.caption(f"Gemini expanded your search to also include: {', '.join(expanded_terms)}")

    if not articles:
        st.warning("No articles matched. Try broader keywords or a longer look-back window.")
        st.stop()

    if fetch_full_text:
        with st.spinner(f"Downloading full text for {min(len(articles), 25)} articles..."):
            articles = enrich_with_full_text(articles)

    with st.spinner("Embedding and clustering articles..."):
        embeddings = embed_articles(articles)
        clusters = cluster_articles(articles, embeddings)

    with st.spinner("Scoring sentiment..."):
        score_articles(articles)

    with st.spinner("Summarizing themes with Gemini..."):
        report = build_report(clusters)
        cluster_sent = cluster_sentiment(clusters)
        for item in report:
            item["avg_sentiment"] = cluster_sent.get(item["cluster_id"], 0.0)

    st.session_state.report = report
    st.session_state.clusters = clusters
    st.session_state.articles = articles
    st.success(f"Analyzed {len(articles)} articles across {len(clusters)} themes.")

report = st.session_state.get("report")

if report:
    tab1, tab2, tab3 = st.tabs(["🗂️ Themes", "📈 Sentiment Trend", "⚖️ Bias / Framing Comparison"])

    with tab1:
        for item in sorted(report, key=lambda r: r["article_count"], reverse=True):
            color, label = theme.sentiment_status(item["avg_sentiment"])
            expander_label = (
                f":{color}[●]  **{item['theme']}**   ·   {item['article_count']} articles"
                f"   ·   :{color}[{label}]"
            )
            with st.expander(expander_label):
                st.write(item["summary"])
                theme.render_source_pills(item["sources"])
                st.metric("Average sentiment", f"{item['avg_sentiment']:.2f}", help="-1 = very negative, +1 = very positive")
                cluster_articles_list = st.session_state.clusters[item["cluster_id"]]
                for a in cluster_articles_list:
                    st.markdown(f"- [{a.title}]({a.link}) — *{a.source}*")

    with tab2:
        trend = sentiment_trend(st.session_state.articles)
        if trend:
            df = pd.DataFrame(trend)
            fig = px.line(df, x="date", y="avg_sentiment", markers=True, title="Average sentiment over time")
            fig.add_hline(y=0, line_dash="dot", line_color="#D2D2D7")
            fig = theme.style_plotly(fig)
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("Not enough date spread to show a trend yet.")

    with tab3:
        st.write("Pick a theme with multiple sources to see how coverage differs.")
        multi_source_clusters = {
            cid: arts for cid, arts in st.session_state.clusters.items()
            if len(set(a.source for a in arts)) >= 2
        }
        if not multi_source_clusters:
            st.info("No theme had 2+ distinct sources in this batch — try a broader topic or more sources.")
        else:
            options = {
                f"{next(r['theme'] for r in report if r['cluster_id'] == cid)} ({len(arts)} articles)": cid
                for cid, arts in multi_source_clusters.items()
            }
            choice = st.selectbox("Theme", list(options.keys()))
            if st.button("Compare framing across sources"):
                with st.spinner("Analyzing framing differences..."):
                    comparison = compare_framing(multi_source_clusters[options[choice]])
                theme.render_framing_card(comparison)
else:
    st.info("Set your topic and sources above, then click **Fetch & Analyze**.")