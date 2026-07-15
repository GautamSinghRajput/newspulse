"""
theme.py
Dark, broadcast-news-inspired visual theme for NewsPulse: near-black
background, a punchy news-red accent, condensed bold headline type, a
centered glowing hero with staggered entrance animations, an ambient
floating background glow, and interactive shine/zoom/glow effects on every
clickable element.

Import and call inject_theme() once near the top of app.py.
"""

import html as _html
import streamlit as st

# ---- Design tokens ------------------------------------------------------
BG = "#0D0D0F"                # near-black page background
BG_SECONDARY = "#1A1A1D"      # card / panel background, dark grey
BG_ELEVATED = "#232326"       # slightly lighter grey for hover states
TEXT_PRIMARY = "#F2F2F2"      # off-white (not pure white — softer on dark)
TEXT_SECONDARY = "#9A9A9E"    # muted grey body text
ACCENT = "#E4002B"            # news red — the one signature accent
ACCENT_HOVER = "#FF1A44"      # brighter red on hover (dark theme brightens, not darkens)
ACCENT_SOFT = "#FF7A59"       # warm secondary tone used only in the gradient title
BORDER = "#2E2E32"            # subtle dark-grey hairline
POSITIVE = "#34D399"          # emerald green, reads clearly on dark
NEGATIVE = "#FF4D4D"          # coral-red, distinct from pure ACCENT so data badges
# don't read as interactive buttons
FONT_STACK = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
HEADLINE_FONT = "'Oswald', 'Helvetica Neue', Arial, sans-serif"

CSS = f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Oswald:wght@500;600;700&family=Inter:wght@400;500;600;700&display=swap');

:root {{
    --bg: {BG};
    --bg-secondary: {BG_SECONDARY};
    --bg-elevated: {BG_ELEVATED};
    --text-primary: {TEXT_PRIMARY};
    --text-secondary: {TEXT_SECONDARY};
    --accent: {ACCENT};
    --accent-hover: {ACCENT_HOVER};
    --accent-soft: {ACCENT_SOFT};
    --border: {BORDER};
    --positive: {POSITIVE};
    --negative: {NEGATIVE};
}}

html, body, [class*="css-"] {{
    font-family: {FONT_STACK};
}}

.block-container {{
    padding-top: 1.5rem;
    max-width: 980px;
    position: relative;
    z-index: 1;
}}
#MainMenu, footer, [data-testid="stToolbar"], [data-testid="stDecoration"] {{
    visibility: hidden;
    display: none;
}}

/* Thin red "on-air" strip across the very top of the viewport */
body::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
    z-index: 999999;
}}

/* ---- Ambient floating background glow ---- */
.np-bg-glow {{
    position: fixed;
    border-radius: 50%;
    filter: blur(100px);
    pointer-events: none;
    z-index: 0;
    opacity: 0.28;
}}
.np-bg-glow-1 {{
    width: 460px; height: 460px;
    background: var(--accent);
    top: -140px; left: -120px;
    animation: np-float-1 20s ease-in-out infinite;
}}
.np-bg-glow-2 {{
    width: 400px; height: 400px;
    background: #4a4a55;
    bottom: -160px; right: -100px;
    animation: np-float-2 24s ease-in-out infinite;
}}
@keyframes np-float-1 {{
    0%, 100% {{ transform: translate(0,0) scale(1); }}
    50%      {{ transform: translate(50px,-50px) scale(1.12); }}
}}
@keyframes np-float-2 {{
    0%, 100% {{ transform: translate(0,0) scale(1); }}
    50%      {{ transform: translate(-40px,40px) scale(1.15); }}
}}

/* Translucent blurred dark header bar */
[data-testid="stHeader"] {{
    background: rgba(13,13,15,0.75);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
}}

h1, h2, h3 {{
    letter-spacing: -0.01em;
    font-weight: 600;
    color: var(--text-primary);
}}

/* ---- Entrance animation ---- */
@keyframes np-fade-up {{
    from {{ opacity: 0; transform: translateY(18px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}

/* ---- Hero: centered, oversized, glowing ---- */
.np-hero {{
    padding: 3.5rem 0 2.25rem 0;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
}}
.np-eyebrow {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    color: var(--accent);
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.9rem;
    font-family: {HEADLINE_FONT};
    animation: np-fade-up 0.6s ease both;
}}
.np-live-dot {{
    display: inline-block;
    width: 8px; height: 8px;
    border-radius: 50%;
    background: var(--accent);
    margin-right: 10px;
    box-shadow: 0 0 0 0 rgba(228,0,43,0.7);
    animation: np-pulse 2s infinite;
}}
@keyframes np-pulse {{
    0%   {{ box-shadow: 0 0 0 0 rgba(228,0,43,0.6); }}
    70%  {{ box-shadow: 0 0 0 9px rgba(228,0,43,0); }}
    100% {{ box-shadow: 0 0 0 0 rgba(228,0,43,0); }}
}}
.np-hero-title {{
    font-family: {HEADLINE_FONT};
    font-size: clamp(3.2rem, 9vw, 6rem);
    font-weight: 700;
    letter-spacing: -0.01em;
    line-height: 1.0;
    text-transform: uppercase;
    margin: 0 0 0.9rem 0;
    background: linear-gradient(100deg, var(--accent) 0%, var(--accent-soft) 45%, var(--text-primary) 100%);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
    text-shadow: 0 0 60px rgba(228,0,43,0.35);
    animation: np-fade-up 0.7s ease both;
    animation-delay: 0.08s;
}}
.np-hero-subtitle {{
    font-size: 1.15rem;
    font-weight: 400;
    color: var(--text-secondary) !important;
    max-width: 620px;
    line-height: 1.55;
    margin: 0 auto;
    animation: np-fade-up 0.7s ease both;
    animation-delay: 0.18s;
}}
.np-divider {{
    position: relative;
    overflow: hidden;
    border: none;
    border-top: 1px solid var(--border);
    margin: 1.75rem 0 0.5rem 0;
}}
.np-divider::after {{
    content: "";
    position: absolute;
    top: -1px; left: -30%;
    width: 30%; height: 2px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    animation: np-scan 3.5s linear infinite;
}}
@keyframes np-scan {{
    0%   {{ left: -30%; }}
    100% {{ left: 100%; }}
}}

/* ---- Settings card ---- */
[data-testid="stVerticalBlockBorderWrapper"] {{
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-secondary);
    box-shadow: 0 4px 24px rgba(0,0,0,0.35);
    padding: 0.25rem 0.5rem;
    animation: np-fade-up 0.5s ease both;
}}
.block-container h5 {{
    font-family: {HEADLINE_FONT};
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-secondary);
    margin-bottom: 0.5rem;
}}

/* ---- Command-bar search input ---- */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div[data-baseweb="select"] > div,
[data-testid="stMultiSelect"] div[data-baseweb="select"] > div {{
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}
[data-testid="stTextInput"] input {{
    font-size: 1.05rem !important;
    font-weight: 500;
    padding: 0.9rem 1rem !important;
    height: auto !important;
}}
[data-testid="stTextInput"] input:focus {{
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(228,0,43,0.2) !important;
}}

/* ---- Multiselect / select tags: neutral grey, red on hover ---- */
[data-baseweb="tag"] {{
    background-color: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    transition: border-color 0.15s ease, transform 0.15s ease;
}}
[data-baseweb="tag"]:hover {{
    border-color: var(--accent) !important;
    transform: translateY(-1px);
}}
[data-baseweb="tag"] span {{
    color: var(--text-primary) !important;
    font-weight: 500;
}}
[data-baseweb="tag"] svg {{
    fill: var(--text-secondary) !important;
}}

/* ---- Buttons: interactive red-glow + shine sweep on hover ---- */
button[kind="primary"] {{
    position: relative;
    overflow: hidden;
    background: var(--accent) !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.85rem 1.1rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-family: {HEADLINE_FONT};
    transition: background 0.15s ease, transform 0.1s ease, box-shadow 0.15s ease;
    animation: np-breathe 2.6s ease-in-out infinite;
}}
@keyframes np-breathe {{
    0%, 100% {{ box-shadow: 0 0 0 rgba(228,0,43,0); }}
    50%      {{ box-shadow: 0 0 22px rgba(228,0,43,0.4); }}
}}
button[kind="primary"]::after {{
    content: "";
    position: absolute;
    top: 0; left: -75%;
    width: 50%; height: 100%;
    background: linear-gradient(120deg, transparent, rgba(255,255,255,0.35), transparent);
    transform: skewX(-20deg);
    transition: left 0.5s ease;
}}
button[kind="primary"]:hover::after {{ left: 125%; }}
button[kind="primary"]:hover {{
    animation: none;
    background: var(--accent-hover) !important;
    transform: translateY(-1px);
    box-shadow: 0 0 28px rgba(228,0,43,0.5);
}}
button[kind="primary"]:active {{
    transform: translateY(0);
    box-shadow: 0 0 8px rgba(228,0,43,0.3);
}}
button[kind="secondary"] {{
    background: var(--bg-elevated) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-primary) !important;
    font-weight: 500 !important;
    transition: border-color 0.15s ease, transform 0.1s ease, color 0.15s ease;
}}
button[kind="secondary"]:hover {{
    border-color: var(--accent) !important;
    color: var(--accent) !important;
    transform: translateY(-1px);
}}

/* ---- Toggle-style checkboxes: feels like a control-panel switch, not a form field ---- */
[data-testid="stCheckbox"] {{
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 0.65rem 0.9rem;
    transition: border-color 0.15s ease;
}}
[data-testid="stCheckbox"]:hover {{
    border-color: var(--accent);
}}

/* ---- Segmented control chips (preset choices) ---- */
[data-testid="stSegmentedControl"] {{
    margin-bottom: 0.4rem;
}}
[data-testid="stSegmentedControl"] label {{
    border-radius: 999px !important;
    transition: border-color 0.15s ease, transform 0.1s ease;
}}
[data-testid="stSegmentedControl"] label:hover {{
    transform: translateY(-1px);
}}

/* ---- Tabs: underline indicator, news-channel-selector style ---- */
[data-testid="stTabs"] [role="tablist"] {{
    background: transparent;
    border-bottom: 1px solid var(--border);
    gap: 1.5rem;
}}
[data-testid="stTabs"] button[role="tab"] {{
    border-radius: 0;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    font-size: 0.85rem;
    color: var(--text-secondary);
    border: none !important;
    border-bottom: 2px solid transparent !important;
    padding-bottom: 0.6rem;
    transition: color 0.15s ease, border-color 0.15s ease;
}}
[data-testid="stTabs"] button[role="tab"]:hover {{
    color: var(--text-primary);
}}
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    background: transparent;
    color: var(--accent);
    border-bottom: 2px solid var(--accent) !important;
    box-shadow: none;
}}
[data-baseweb="tab-highlight"] {{ display: none; }}

/* ---- Expander cards ---- */
[data-testid="stExpander"] {{
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    background: var(--bg-secondary);
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    margin-bottom: 0.75rem;
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    overflow: hidden;
    animation: np-fade-up 0.5s ease both;
}}
[data-testid="stExpander"]:hover {{
    border-color: var(--accent) !important;
    box-shadow: 0 10px 32px rgba(228,0,43,0.18);
    transform: translateY(-2px);
}}
[data-testid="stExpander"] summary {{
    font-weight: 500;
    padding: 0.9rem 1.1rem;
    color: var(--text-primary);
}}

/* ---- Metrics ---- */
[data-testid="stMetricValue"] {{
    font-family: {HEADLINE_FONT};
    font-size: 1.8rem;
    font-weight: 600;
    color: var(--text-primary);
}}
[data-testid="stMetricLabel"] {{
    color: var(--text-secondary);
    font-weight: 500;
}}

/* ---- Alerts: quiet left-border style ---- */
[data-testid="stAlert"] {{
    background: var(--bg-secondary) !important;
    border-radius: 8px;
    border: none;
    border-left: 3px solid var(--accent);
    color: var(--text-primary);
    animation: np-fade-up 0.4s ease both;
}}

/* ---- Source pills ---- */
.np-pill-row {{ margin: 0.6rem 0; }}
.np-pill {{
    display: inline-block;
    padding: 3px 12px;
    margin: 2px 6px 2px 0;
    background: var(--bg-elevated);
    border: 1px solid var(--border);
    color: var(--text-secondary);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 500;
    transition: border-color 0.15s ease;
}}
.np-pill:hover {{ border-color: var(--accent); }}

/* ---- Headline preview cards ---- */
.np-headline-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin: 0.5rem 0 1rem 0;
}}
@media (max-width: 800px) {{
    .np-headline-grid {{ grid-template-columns: repeat(2, 1fr); }}
}}
@media (max-width: 480px) {{
    .np-headline-grid {{ grid-template-columns: 1fr; }}
}}
.np-headline-grid > a {{
    display: block;
    animation: np-fade-up 0.55s ease both;
}}
.np-headline-grid > a:nth-child(1) {{ animation-delay: 0.02s; }}
.np-headline-grid > a:nth-child(2) {{ animation-delay: 0.08s; }}
.np-headline-grid > a:nth-child(3) {{ animation-delay: 0.14s; }}
.np-headline-grid > a:nth-child(4) {{ animation-delay: 0.20s; }}
.np-headline-grid > a:nth-child(5) {{ animation-delay: 0.26s; }}
.np-headline-grid > a:nth-child(6) {{ animation-delay: 0.32s; }}
.np-headline-grid > a:nth-child(7) {{ animation-delay: 0.38s; }}
.np-headline-grid > a:nth-child(8) {{ animation-delay: 0.44s; }}
.np-headline-card {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3);
    transition: border-color 0.2s ease, box-shadow 0.2s ease, transform 0.2s ease;
    display: flex;
    flex-direction: column;
}}
.np-headline-card:hover {{
    border-color: var(--accent);
    box-shadow: 0 10px 32px rgba(228,0,43,0.22);
    transform: translateY(-3px);
}}
.np-headline-card a {{ text-decoration: none !important; color: inherit !important; }}
.np-headline-img-wrap {{
    width: 100%;
    aspect-ratio: 16 / 10;
    background: var(--bg-elevated);
    overflow: hidden;
}}
.np-headline-img-wrap img {{
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.4s ease;
}}
.np-headline-card:hover .np-headline-img-wrap img {{
    transform: scale(1.08);
}}
.np-headline-body {{ padding: 0.9rem 1rem 1.1rem 1rem; }}
.np-headline-source {{
    font-family: {HEADLINE_FONT};
    font-size: 0.7rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent);
    margin-bottom: 0.3rem;
}}
.np-headline-title {{
    font-size: 0.92rem;
    font-weight: 600;
    line-height: 1.35;
    color: var(--text-primary) !important;
}}

/* ---- Framing comparison: evidence strip + structured sections ---- */
.np-evidence-strip {{
    display: flex;
    flex-direction: column;
    gap: 0.6rem;
    margin: 0.75rem 0 1.25rem 0;
}}
.np-evidence-row {{
    display: flex;
    align-items: baseline;
    gap: 0.75rem;
    padding: 0.7rem 1rem;
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-left: 3px solid var(--accent);
    border-radius: 8px;
    transition: border-color 0.15s ease, transform 0.15s ease;
}}
.np-evidence-row:hover {{
    border-color: var(--accent);
    transform: translateX(2px);
}}
.np-evidence-source {{
    font-family: {HEADLINE_FONT};
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: var(--accent);
    white-space: nowrap;
    flex-shrink: 0;
    min-width: 130px;
}}
.np-evidence-title {{
    font-size: 0.92rem;
    color: var(--text-primary) !important;
    line-height: 1.4;
}}
.np-framing-verdict {{
    background: var(--bg-elevated);
    border-radius: 8px;
    padding: 0.9rem 1.2rem;
    font-size: 0.95rem;
    font-weight: 500;
    color: var(--text-primary);
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
}}
.np-framing-grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
    gap: 0.9rem;
}}
.np-framing-section {{
    background: var(--bg-secondary);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    animation: np-fade-up 0.5s ease both;
    transition: border-color 0.2s ease, transform 0.2s ease;
}}
.np-framing-section:hover {{
    border-color: var(--accent);
    transform: translateY(-2px);
}}
.np-framing-section-label {{
    font-family: {HEADLINE_FONT};
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.06em;
    color: var(--accent);
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.4rem;
}}
.np-framing-section-body {{
    font-size: 0.92rem;
    line-height: 1.55;
    color: var(--text-primary);
}}

a {{ color: var(--accent) !important; text-decoration: none; transition: color 0.15s ease; }}
a:hover {{ color: var(--accent-hover) !important; text-decoration: underline; }}

@media (prefers-reduced-motion: reduce) {{
    * {{ transition: none !important; animation: none !important; }}
}}
:focus-visible {{ outline: 2px solid var(--accent) !important; outline-offset: 2px; }}
</style>
"""

# Kept as a plain single-line string (not inside the indented CSS block
# above) so Markdown never mistakes it for an indented code block — see
# render_headline_cards() docstring for why indentation matters here.
BG_ORBS_HTML = '<div class="np-bg-glow np-bg-glow-1"></div><div class="np-bg-glow np-bg-glow-2"></div>'


def inject_theme():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(BG_ORBS_HTML, unsafe_allow_html=True)


def render_hero(eyebrow: str, title: str, subtitle: str):
    html_str = (
        f'<div class="np-hero">'
        f'<div class="np-eyebrow"><span class="np-live-dot"></span>{_html.escape(eyebrow)}</div>'
        f'<h1 class="np-hero-title">{_html.escape(title)}</h1>'
        f'<p class="np-hero-subtitle">{_html.escape(subtitle)}</p>'
        f'</div><hr class="np-divider">'
    )
    st.markdown(html_str, unsafe_allow_html=True)


def sentiment_status(score: float):
    """Returns (streamlit_color_name, label) for a sentiment score."""
    if score > 0.1:
        return "green", "Positive"
    if score < -0.1:
        return "red", "Negative"
    return "gray", "Neutral"


def render_source_pills(sources):
    spans = "".join(f'<span class="np-pill">{_html.escape(s)}</span>' for s in sources)
    st.markdown(f'<div class="np-pill-row">{spans}</div>', unsafe_allow_html=True)


def render_headline_cards(articles):
    """
    Renders a responsive grid of headline preview cards with thumbnails,
    staggered fade-up entrance animation, and a hover image-zoom effect.
    Falls back to a plain placeholder block (no broken-image icon) if an
    article had no extractable image.

    IMPORTANT: every HTML fragment here is built as a single unbroken line
    with no leading whitespace. Markdown treats lines indented by 4+ spaces
    as a literal code block, so a "nicely indented" multi-line f-string
    would render as visible raw HTML instead of an actual card.
    """
    cards = []
    for a in articles:
        title = _html.escape(a.title)
        source = _html.escape(a.source)
        link = _html.escape(a.link, quote=True)
        if a.image:
            img_html = (
                f'<img src="{_html.escape(a.image, quote=True)}" alt="" '
                f'onerror="this.parentElement.style.display=\'none\'">'
            )
        else:
            img_html = ""
        card_html = (
            f'<a href="{link}" target="_blank" rel="noopener noreferrer">'
            f'<div class="np-headline-card">'
            f'<div class="np-headline-img-wrap">{img_html}</div>'
            f'<div class="np-headline-body">'
            f'<div class="np-headline-source">{source}</div>'
            f'<div class="np-headline-title">{title}</div>'
            f'</div></div></a>'
        )
        cards.append(card_html)
    st.markdown(f'<div class="np-headline-grid">{"".join(cards)}</div>', unsafe_allow_html=True)


def render_framing_comparison(articles, framing):
    """
    Renders the framing/bias comparison as:
    1. An evidence strip showing each source's actual headline (grounds the
       analysis in something concrete the user can verify/click into)
    2. A one-line verdict callout
    3. Three labeled sections (emphasis / tone / omitted facts) instead of
       one undifferentiated paragraph

    Defensive: if `framing` comes back as a plain string (e.g. an older
    version of summarize.compare_framing that hadn't been updated yet),
    display it as a simple fallback instead of crashing on .get().

    All HTML built as single unbroken lines — see render_headline_cards()
    docstring for why indentation would break rendering here.
    """
    if isinstance(framing, str):
        st.markdown(f'<div class="np-framing-verdict">{_html.escape(framing)}</div>', unsafe_allow_html=True)
        st.caption("⚠️ Your summarize.py looks out of date — compare_framing() should return a dict, "
                   "not a string. Re-copy the latest summarize.py for the structured breakdown.")
        return

    rows = []
    for a in articles[:4]:
        source = _html.escape(a.source)
        title = _html.escape(a.title)
        link = _html.escape(a.link, quote=True)
        rows.append(
            f'<div class="np-evidence-row">'
            f'<span class="np-evidence-source">{source}</span>'
            f'<a class="np-evidence-title" href="{link}" target="_blank" rel="noopener noreferrer">{title}</a>'
            f'</div>'
        )
    st.markdown(f'<div class="np-evidence-strip">{"".join(rows)}</div>', unsafe_allow_html=True)

    if not framing.get("available"):
        st.warning("Gemini's framing analysis didn't come back in the expected format — try again.")
        return

    verdict = _html.escape(framing.get("verdict", ""))
    if verdict:
        st.markdown(f'<div class="np-framing-verdict">⚖️ {verdict}</div>', unsafe_allow_html=True)

    sections = [
        ("📍", "Emphasis", framing.get("emphasis", "")),
        ("🗣️", "Tone &amp; Word Choice", framing.get("tone", "")),
        ("🔍", "Omitted Facts", framing.get("omitted", "")),
    ]
    blocks = []
    for icon, label, body in sections:
        if not body:
            continue
        safe_body = _html.escape(body)
        blocks.append(
            f'<div class="np-framing-section">'
            f'<div class="np-framing-section-label">{icon} {label}</div>'
            f'<div class="np-framing-section-body">{safe_body}</div>'
            f'</div>'
        )
    st.markdown(f'<div class="np-framing-grid">{"".join(blocks)}</div>', unsafe_allow_html=True)


def style_plotly(fig, force_accent_color: bool = True):
    fig.update_layout(
        font=dict(family=FONT_STACK, size=13, color=TEXT_PRIMARY),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=40, b=10),
        hoverlabel=dict(bgcolor=BG_SECONDARY, font_family=FONT_STACK, bordercolor=BORDER, font_color=TEXT_PRIMARY),
    )
    if force_accent_color:
        fig.update_traces(line_color=ACCENT, marker=dict(color=ACCENT, size=7))
    fig.update_xaxes(showgrid=False, showline=True, linecolor=BORDER, ticks="outside", tickcolor=BORDER, color=TEXT_SECONDARY)
    fig.update_yaxes(showgrid=True, gridcolor=BG_SECONDARY, zeroline=True, zerolinecolor=BORDER, color=TEXT_SECONDARY)
    return fig