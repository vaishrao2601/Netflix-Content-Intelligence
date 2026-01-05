import math
import html
import textwrap
import numpy as np
import pandas as pd
import requests
import streamlit as st

import plotly.express as px
import plotly.graph_objects as go


# -------------------- CONFIG (MUST be first Streamlit call) --------------------
st.set_page_config(
    page_title="Netflix Content Intelligence",
    page_icon="🎬",
    layout="wide",
)

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = st.secrets["TMDB_API_KEY"]
IMG_BASE = "https://image.tmdb.org/t/p/w500"


# -------------------- THEME + UI CSS --------------------
NETFLIX_RED = "#E50914"
BG = "#0B0B0F"
CARD = "rgba(255,255,255,0.06)"
CARD_BORDER = "rgba(255,255,255,0.10)"
TEXT = "rgba(255,255,255,0.92)"
MUTED = "rgba(255,255,255,0.65)"

st.markdown(
    f"""
<style>
/* Hide Streamlit top header white bar */
[data-testid="stHeader"], [data-testid="stToolbar"] {{
  background: {BG} !important;
}}
#MainMenu {{visibility: hidden;}}
footer {{visibility: hidden;}}

/* App background */
.stApp {{
  background: radial-gradient(1200px 700px at 20% 10%, rgba(229,9,20,0.18), transparent 55%),
              radial-gradient(900px 500px at 90% 30%, rgba(255,255,255,0.06), transparent 60%),
              {BG};
  color: {TEXT};
}}

/* Global text */
h1,h2,h3,h4,h5,h6,p,span,div {{
  color: {TEXT};
}}

/* Make any accidental markdown code blocks readable on dark theme */
pre, code {{
  background: rgba(20,20,26,0.92) !important;
  color: rgba(255,255,255,0.88) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.10) !important;
}}
pre {{
  padding: 12px 14px !important;
  overflow-x: auto !important;
}}

/* Sidebar */
section[data-testid="stSidebar"] {{
  background: rgba(10,10,14,0.96) !important;
  border-right: 1px solid rgba(255,255,255,0.06);
}}
.sidebar-brand {{
  font-size: 28px;
  font-weight: 800;
  line-height: 1.05;
  color: rgba(255,255,255,0.92);
}}
.sidebar-sub {{
  margin-top: 6px;
  font-size: 14px;
  color: rgba(255,255,255,0.60);
}}
.sidebar-section {{
  margin-top: 16px;
  font-size: 18px;
  font-weight: 800;
  color: rgba(255,255,255,0.88);
}}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stMarkdown,
section[data-testid="stSidebar"] span {{
  color: rgba(255,255,255,0.80) !important;
}}

/* Cards */
.nx-card {{
  background: {CARD};
  border: 1px solid {CARD_BORDER};
  border-radius: 18px;
  padding: 18px 18px;
  box-shadow: 0 18px 45px rgba(0,0,0,0.45);
}}
.nx-header {{
  background: {CARD};
  border: 1px solid {CARD_BORDER};
  border-radius: 22px;
  padding: 18px 20px;
  box-shadow: 0 18px 50px rgba(0,0,0,0.55);
  position: relative;
}}
.nx-header:before {{
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  width: 4px;
  height: 100%;
  background: {NETFLIX_RED};
  border-radius: 22px 0 0 22px;
}}

/* Metric cards */
.metric-title {{
  font-size: 12px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255,255,255,0.60);
  margin-bottom: 6px;
}}
.metric-value {{
  font-size: 36px;
  font-weight: 900;
  color: {NETFLIX_RED};
  line-height: 1.0;
}}
.metric-sub {{
  margin-top: 6px;
  color: rgba(255,255,255,0.55);
  font-size: 12px;
}}

/* Pills */
.pill {{
  display:inline-block;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.02em;
  border: 1px solid rgba(255,255,255,0.14);
}}
.pill-low {{ background: rgba(46, 204, 113, 0.16); color: rgba(255,255,255,0.92); border-color: rgba(46, 204, 113, 0.35); }}
.pill-med {{ background: rgba(241, 196, 15, 0.14); color: rgba(255,255,255,0.92); border-color: rgba(241, 196, 15, 0.35); }}
.pill-high {{ background: rgba(231, 76, 60, 0.14); color: rgba(255,255,255,0.92); border-color: rgba(231, 76, 60, 0.35); }}

/* Clickable posters */
a.poster-link img {{
  border-radius: 16px;
  transition: transform 0.18s ease, box-shadow 0.18s ease;
}}
a.poster-link img:hover {{
  transform: translateY(-6px) scale(1.02);
  box-shadow: 0 18px 40px rgba(0,0,0,0.55);
}}

/* -------------------- SELECTBOX + DROPDOWN MENU FIX (DARK GREY, WHITE TEXT, RED HOVER) -------------------- */

/* Control (closed state) */
div[data-baseweb="select"] > div {{
  background: rgba(20,20,26,0.98) !important;
  border-radius: 12px !important;
  border: 1px solid rgba(255,255,255,0.16) !important;
  box-shadow: 0 10px 25px rgba(0,0,0,0.35) !important;
}}

/* Text + icons inside control */
div[data-baseweb="select"] span,
div[data-baseweb="select"] input,
div[data-baseweb="select"] svg {{
  color: rgba(255,255,255,0.92) !important;
}}

/* Placeholder text */
div[data-baseweb="select"] [data-testid="stMarkdownContainer"] {{
  color: rgba(255,255,255,0.62) !important;
}}

/* Popover container (OPEN dropdown menu) */
div[data-baseweb="popover"] > div {{
  background: rgba(20,20,26,0.98) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  border-radius: 14px !important;
  overflow: hidden !important;
  box-shadow: 0 18px 55px rgba(0,0,0,0.55) !important;
}}

/* Menu list background */
ul[role="listbox"] {{
  background: rgba(20,20,26,0.98) !important;
}}

/* Menu option default */
li[role="option"] {{
  background: rgba(20,20,26,0.98) !important;
  color: rgba(255,255,255,0.92) !important;
}}

/* Hover = light red background, white text */
li[role="option"]:hover {{
  background: rgba(229,9,20,0.32) !important;
  color: rgba(255,255,255,0.95) !important;
}}

/* Selected = slightly stronger light red */
li[role="option"][aria-selected="true"] {{
  background: rgba(229,9,20,0.38) !important;
  color: rgba(255,255,255,0.95) !important;
}}

/* Slider label */
[data-testid="stSlider"] {{
  color: rgba(255,255,255,0.85) !important;
}}
</style>
""",
    unsafe_allow_html=True,
)


# -------------------- HELPERS --------------------
def clickable_poster(poster_url: str, tmdb_url: str, alt: str = "", height_px: int = 340):
    alt = html.escape(alt or "")
    st.markdown(
        f"""
        <a class="poster-link" href="{tmdb_url}" target="_blank" rel="noopener noreferrer" style="text-decoration:none;">
            <img src="{poster_url}" alt="{alt}"
                 style="width:100%; height:{height_px}px; object-fit:cover; border-radius:16px;">
        </a>
        """,
        unsafe_allow_html=True
    )

def metric_card(title: str, value: str, subtitle: str = ""):
    st.markdown(
        f"""
        <div class="nx-card">
          <div class="metric-title">{html.escape(title)}</div>
          <div class="metric-value">{html.escape(str(value))}</div>
          <div class="metric-sub">{html.escape(str(subtitle))}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def info_card(title: str, body_html: str):
    # KEY FIX: your “white boxes” were Markdown code blocks caused by indentation
    # in triple-quoted strings. Dedenting prevents Streamlit from rendering them as code.
    body_html = textwrap.dedent(body_html).strip()
    st.markdown(
        f"""
        <div class="nx-card">
          <div style="font-size:16px; font-weight:900; color:{TEXT};">{html.escape(title)}</div>
          <div style="margin-top:10px; color:{MUTED}; line-height:1.65; font-size:14px;">
            {body_html}
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def pill(text: str, level: str = "low"):
    cls = {"low":"pill-low","med":"pill-med","high":"pill-high"}.get(level, "pill-low")
    return f'<span class="pill {cls}">{html.escape(text)}</span>'

def safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default

def zscore(s: pd.Series) -> pd.Series:
    s = pd.to_numeric(s, errors="coerce")
    mu = s.mean()
    sd = s.std(ddof=0)
    if sd == 0 or np.isnan(sd):
        return pd.Series([0]*len(s), index=s.index)
    return (s - mu) / sd

def clamp01(x: float) -> float:
    return float(max(0.0, min(1.0, x)))

def sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

def norm_0_100(val, vmin, vmax):
    if vmax == vmin:
        return 50.0
    return float(100.0 * (val - vmin) / (vmax - vmin))

def _inv_genre_map(genre_map_in: dict) -> dict:
    return {v: k for k, v in genre_map_in.items()}

def _explode_genres_movies(df_in: pd.DataFrame, genre_map_in: dict) -> pd.DataFrame:
    inv = _inv_genre_map(genre_map_in)
    rows = []
    for _, r in df_in.iterrows():
        gids = r.get("genre_ids") or []
        if not gids:
            rows.append({**r.to_dict(), "genre": "Unknown"})
        else:
            for gid in gids:
                rows.append({**r.to_dict(), "genre": inv.get(gid, "Unknown")})
    return pd.DataFrame(rows)

def _robust_lin_forecast(x: np.ndarray, y: np.ndarray, x_future: np.ndarray):
    if len(x) < 3 or np.all(np.isnan(y)) or np.nanstd(y) == 0:
        yhat = np.full_like(x_future, float(np.nanmean(y) if len(y) else 0.0), dtype=float)
        sigma = float(np.nanstd(y) if len(y) else 0.0)
        return yhat, sigma
    m = np.isfinite(x) & np.isfinite(y)
    x2, y2 = x[m], y[m]
    if len(x2) < 3:
        yhat = np.full_like(x_future, float(np.nanmean(y2) if len(y2) else 0.0), dtype=float)
        sigma = float(np.nanstd(y2) if len(y2) else 0.0)
        return yhat, sigma
    a, b = np.polyfit(x2, y2, 1)
    y_fit = a * x2 + b
    resid = y2 - y_fit
    sigma = float(np.nanstd(resid)) if len(resid) else 0.0
    yhat = a * x_future + b
    return yhat.astype(float), sigma

def _opportunity_score_for_slice(d: pd.DataFrame) -> float:
    if d.empty:
        return 0.0
    pop = float(d["popularity"].mean())
    rat = float(d["vote_average"].mean())
    eng = float(d["engagement"].mean())
    vol = float(len(d))
    votes = float(np.log1p(d["vote_count"]).mean())
    return (1.10 * pop) + (18.0 * rat) + (22.0 * eng) + (10.0 * votes) - (0.35 * vol)

def _winner(a: float, b: float, higher_is_better: bool = True) -> str:
    if not np.isfinite(a) and not np.isfinite(b):
        return "—"
    if not np.isfinite(a):
        return "B"
    if not np.isfinite(b):
        return "A"
    if higher_is_better:
        return "A" if a >= b else "B"
    return "A" if a <= b else "B"


# -------------------- DATA LOADERS --------------------
@st.cache_data(show_spinner=False)
def load_popular_movies(pages: int = 5) -> pd.DataFrame:
    movies = []
    for page in range(1, pages + 1):
        r = requests.get(
            f"{BASE_URL}/movie/popular",
            params={"api_key": API_KEY, "language": "en-US", "page": page},
            timeout=30
        )
        r.raise_for_status()
        movies.extend(r.json().get("results", []))
    return pd.DataFrame(movies)

@st.cache_data(show_spinner=False)
def load_genres() -> dict:
    r = requests.get(
        f"{BASE_URL}/genre/movie/list",
        params={"api_key": API_KEY, "language": "en-US"},
        timeout=30
    )
    r.raise_for_status()
    genres = r.json().get("genres", [])
    return {g["name"]: g["id"] for g in genres if "name" in g and "id" in g}

def enrich_df(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["poster_url"] = df["poster_path"].apply(lambda p: f"{IMG_BASE}{p}" if pd.notna(p) and p else None)
    df["release_year"] = df["release_date"].astype(str).str[:4]
    df["release_year_num"] = pd.to_numeric(df["release_year"], errors="coerce")
    df["release_month"] = pd.to_datetime(df["release_date"], errors="coerce").dt.month

    df["vote_count"] = pd.to_numeric(df["vote_count"], errors="coerce").fillna(0)
    df["vote_average"] = pd.to_numeric(df["vote_average"], errors="coerce").fillna(0)
    df["popularity"] = pd.to_numeric(df["popularity"], errors="coerce").fillna(0)

    df["log_vote_count"] = np.log1p(df["vote_count"])
    df["netflix_score"] = df["popularity"] + df["vote_average"] + df["log_vote_count"]
    df["engagement"] = (0.65 * df["log_vote_count"]) + (0.35 * df["vote_average"])
    return df


# -------------------- SIDEBAR: BRAND + NAV + GLOBAL FILTERS --------------------
st.sidebar.markdown(
    """
    <div class="sidebar-brand">🎬 Netflix Intelligence</div>
    <div class="sidebar-sub">Content Analytics Platform</div>
    <hr style="border-color: rgba(255,255,255,0.08); margin: 14px 0;">
    """,
    unsafe_allow_html=True
)

page = st.sidebar.radio(
    "Navigation",
    [
        "Content Universe",
        "Performance Deep Dive",
        "Market Opportunities",
        "Recommendation Copilot",
        "Predictive Forecasting",
        "Head-to-Head Comparison",
    ],
    index=0
)

st.sidebar.markdown('<div class="sidebar-section">🔎 Global Filters</div>', unsafe_allow_html=True)

df_raw = load_popular_movies(pages=5)
df = enrich_df(df_raw)

genre_map = load_genres()
genre_options = ["All"] + sorted(genre_map.keys())

selected_genre = st.sidebar.selectbox("Genre", genre_options, index=0)
selected_genre_id = None if selected_genre == "All" else genre_map.get(selected_genre)

min_year = safe_int(df["release_year_num"].dropna().min(), 1980)
max_year = safe_int(df["release_year_num"].dropna().max(), 2025)

year_min, year_max = st.sidebar.slider(
    "Release Year",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
    step=1
)

sort_choice = st.sidebar.selectbox(
    "Sort by",
    ["Netflix Score", "Popularity", "Rating", "Votes"],
    index=0
)

filtered_df = df[
    (df["release_year_num"] >= year_min) &
    (df["release_year_num"] <= year_max)
].copy()

if selected_genre_id is not None:
    filtered_df = filtered_df[filtered_df["genre_ids"].apply(lambda ids: selected_genre_id in (ids or []))].copy()

if filtered_df.empty:
    st.warning("No titles match your filters. Try widening year range or choosing a different genre.")
    st.stop()


# -------------------- TOP HEADER --------------------
st.markdown(
    f"""
    <div class="nx-header">
      <div style="display:flex; align-items:center; gap:14px;">
        <div style="font-size:40px;">🎬</div>
        <div>
          <div style="font-size:34px; font-weight:900; margin:0;">Netflix Content Intelligence</div>
          <div style="color:{MUTED}; margin-top:4px; font-size:14px;">
            Powered by TMDB (live) • Explore content performance & investment signals
          </div>
        </div>
      </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.success(f"Loaded {len(df)} movies from TMDB • Showing {len(filtered_df)} after filters")


# -------------------- SORTING --------------------
def get_sorted(df_in: pd.DataFrame) -> pd.DataFrame:
    if sort_choice == "Popularity":
        return df_in.sort_values("popularity", ascending=False).reset_index(drop=True)
    if sort_choice == "Rating":
        return df_in.sort_values("vote_average", ascending=False).reset_index(drop=True)
    if sort_choice == "Votes":
        return df_in.sort_values("vote_count", ascending=False).reset_index(drop=True)
    return df_in.sort_values("netflix_score", ascending=False).reset_index(drop=True)

browse_df = get_sorted(filtered_df)


# ======================================================================================
# PAGES
# ======================================================================================

def page_content_universe(df_use: pd.DataFrame):
    st.markdown("## 🌍 Content Universe Overview")
    st.caption("A fast, executive snapshot of what exists in the catalog and where the momentum is.")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        metric_card("TOTAL TITLES", f"{len(df_use):,}", "After global filters")
    with c2:
        metric_card("AVG RATING", f"{df_use['vote_average'].mean():.1f}/10", "Quality signal")
    with c3:
        metric_card("TOTAL VOTES", f"{int(df_use['vote_count'].sum()):,}", "Engagement proxy")
    with c4:
        metric_card("AVG POPULARITY", f"{df_use['popularity'].mean():.1f}", "Reach signal")

    st.markdown("---")

    left, right = st.columns([1.1, 1.0], gap="large")

    with left:
        st.markdown("### 🎭 Top Genres by Volume")
        inv_genre = {v: k for k, v in genre_map.items()}
        rows = []
        for _, r in df_use.iterrows():
            for gid in (r.get("genre_ids") or []):
                rows.append(inv_genre.get(gid, "Unknown"))
        if rows:
            gcounts = pd.Series(rows).value_counts().head(10).reset_index()
            gcounts.columns = ["genre", "titles"]
            fig = px.bar(gcounts, x="titles", y="genre", orientation="h")
            fig.update_layout(
                height=420,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="rgba(255,255,255,0.85)"),
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No genre data available for current filters.")

    with right:
        st.markdown("### 💥 Popularity vs Quality")
        d = df_use.copy()
        d["log_popularity"] = np.log1p(d["popularity"])
        fig = px.scatter(
            d,
            x="vote_average",
            y="log_popularity",
            size="vote_count",
            hover_data=["title", "release_date"],
        )
        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig.update_xaxes(title="Avg Rating (Quality)")
        fig.update_yaxes(title="Log(Popularity + 1) (Reach)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🔥 Top Picks (Netflix Score)")

    top_picks = df_use.sort_values("netflix_score", ascending=False).head(10).reset_index(drop=True)
    cols_per_row = 5
    rows = math.ceil(len(top_picks) / cols_per_row)

    for r in range(rows):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            i = r * cols_per_row + c
            if i >= len(top_picks):
                break
            m = top_picks.iloc[i]
            with cols[c]:
                if m["poster_url"]:
                    tmdb_url = f"https://www.themoviedb.org/movie/{int(m['id'])}"
                    clickable_poster(m["poster_url"], tmdb_url, alt=m["title"], height_px=320)
                st.markdown(f"**{m['title']}**")
                st.caption(f"{m['release_year']} · ⭐ {m['vote_average']:.1f} · 🔥 {m['netflix_score']:.2f}")

    st.markdown("---")
    st.markdown("### 🍿 Browse (Sorted by your choice)")
    st.caption("Click posters to open TMDB. Sorting uses the left filter panel.")

    cols_per_row = 5
    rows = math.ceil(len(df_use) / cols_per_row)
    for r in range(min(rows, 8)):
        cols = st.columns(cols_per_row)
        for c in range(cols_per_row):
            i = r * cols_per_row + c
            if i >= len(df_use):
                break
            m = df_use.iloc[i]
            with cols[c]:
                if m["poster_url"]:
                    tmdb_url = f"https://www.themoviedb.org/movie/{int(m['id'])}"
                    clickable_poster(m["poster_url"], tmdb_url, alt=m["title"], height_px=280)
                st.markdown(f"**{m['title']}**")
                st.caption(f"{m['release_year']} · ⭐ {m['vote_average']:.1f}")
                st.caption(f"🔥 Score {m['netflix_score']:.2f} · 👥 {int(m['vote_count']):,}")


def page_performance_deep_dive(df_use: pd.DataFrame):
    st.markdown("## 📊 Performance Deep Dive")
    st.caption("Find what drives wins: anomalies, drivers, and engagement behavior — with drilldowns you can explain in a demo.")

    cc1, cc2, cc3 = st.columns([0.38, 0.32, 0.30])
    with cc1:
        anomaly_strength = st.slider("Anomaly sensitivity (higher = fewer anomalies)", 1.5, 4.0, 2.5, 0.1)
    with cc2:
        anomaly_metric = st.selectbox("Anomaly metric", ["Popularity", "Netflix Score", "Votes"], index=0)
    with cc3:
        color_metric = st.selectbox("Color by", ["Rating", "Votes", "Netflix Score"], index=2)

    d = df_use.copy()

    if anomaly_metric == "Netflix Score":
        base = d["netflix_score"]
    elif anomaly_metric == "Votes":
        base = d["vote_count"]
    else:
        base = d["popularity"]

    base_log = np.log1p(pd.to_numeric(base, errors="coerce").fillna(0))
    d["anomaly_z"] = zscore(base_log)
    d["is_anomaly"] = d["anomaly_z"].abs() >= anomaly_strength

    top = d.sort_values("netflix_score", ascending=False).head(1)
    top_title = top["title"].iloc[0] if len(top) else "—"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("TOP PERFORMER", f"{top_title[:16]}…" if len(top_title) > 18 else top_title, "Netflix Score leader")
    with k2:
        metric_card("PEAK POPULARITY", f"{d['popularity'].max():.1f}", "Max reach within filter")
    with k3:
        metric_card("AVG ENGAGEMENT", f"{d['engagement'].mean():.2f}", "Engagement proxy")
    with k4:
        metric_card("ANOMALIES", f"{int(d['is_anomaly'].sum())}", f"±{anomaly_strength}σ (log scale)")

    st.markdown("---")

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("### 🔍 Popularity vs Rating (Anomaly Lens)")
        if color_metric == "Rating":
            color = d["vote_average"]
        elif color_metric == "Votes":
            color = np.log1p(d["vote_count"])
        else:
            color = d["netflix_score"]

        d_plot = d.copy()
        d_plot["log_popularity"] = np.log1p(d_plot["popularity"])

        fig = px.scatter(
            d_plot,
            x="vote_average",
            y="log_popularity",
            size=np.clip(d_plot["vote_count"], 1, None),
            color=color,
            hover_data=["title", "release_date", "vote_count", "netflix_score"],
            symbol="is_anomaly",
        )
        fig.update_layout(
            height=480,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        fig.update_xaxes(title="Rating (Quality)", gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(title="Log(Popularity + 1)", gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### 🧠 What Actually Drives Reach?")
        corr_df = d[["popularity", "vote_average", "vote_count", "netflix_score", "engagement"]].copy()
        corr = corr_df.corr(numeric_only=True)

        pop_corr_votes = corr.loc["popularity", "vote_count"]
        pop_corr_rating = corr.loc["popularity", "vote_average"]
        pop_corr_score = corr.loc["popularity", "netflix_score"]

        info_card(
            "Driver Summary",
            f"""
<ul style="margin:0; padding-left:18px;">
  <li>Votes → Popularity correlation: <b style="color:{NETFLIX_RED};">{pop_corr_votes:+.2f}</b></li>
  <li>Rating → Popularity correlation: <b style="color:{NETFLIX_RED};">{pop_corr_rating:+.2f}</b></li>
  <li>Netflix Score → Popularity correlation: <b style="color:{NETFLIX_RED};">{pop_corr_score:+.2f}</b></li>
</ul>
<div style="margin-top:10px;">
  <i>Interpretation:</i> votes behave like an engagement proxy; rating behaves like a quality proxy.
  Netflix Score blends both and usually tracks reach better than rating alone.
</div>
"""
        )

        fig = px.imshow(
            corr.round(2),
            text_auto=True,
            aspect="auto",
            color_continuous_scale="YlOrRd",
        )
        fig.update_layout(
            height=360,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    st.markdown("### 🧾 Anomalies (Explainable List)")
    st.caption("Titles that deviate from typical behavior given your filter window.")

    anoms = d[d["is_anomaly"]].copy()
    anoms = anoms.sort_values("anomaly_z", key=lambda s: s.abs(), ascending=False)
    show_n = st.slider("How many anomalies to show", 3, 25, 10, 1)

    anoms_show = anoms.head(show_n)[["title", "release_date", "vote_average", "vote_count", "popularity", "netflix_score", "anomaly_z", "poster_url", "id"]]

    if anoms_show.empty:
        st.info("No anomalies at this sensitivity. Lower the sensitivity slider to see more.")
    else:
        st.dataframe(
            anoms_show.drop(columns=["poster_url", "id"]),
            use_container_width=True
        )

        st.markdown("#### 🎬 Quick anomaly posters")
        cols = st.columns(min(5, len(anoms_show)))
        for i, (_, row) in enumerate(anoms_show.head(5).iterrows()):
            with cols[i]:
                if row["poster_url"]:
                    tmdb_url = f"https://www.themoviedb.org/movie/{int(row['id'])}"
                    clickable_poster(row["poster_url"], tmdb_url, alt=row["title"], height_px=260)
                st.caption(f"**{row['title']}**")
                st.caption(f"z={row['anomaly_z']:+.2f} · 🔥 {row['netflix_score']:.2f}")

    st.markdown("---")

    st.markdown("### 🗓️ Release Window Signals")
    st.caption("Lightweight pattern story using release month in the TMDB popular feed.")

    season = d.dropna(subset=["release_month"]).copy()
    if season.empty:
        st.info("No release month data available for current filters.")
        return

    month_map = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"May",6:"Jun",7:"Jul",8:"Aug",9:"Sep",10:"Oct",11:"Nov",12:"Dec"}
    season["month_name"] = season["release_month"].map(month_map)

    grp = season.groupby("month_name", as_index=False).agg(
        avg_popularity=("popularity", "mean"),
        avg_score=("netflix_score", "mean"),
        titles=("title", "count"),
    )
    grp["month_order"] = grp["month_name"].map({v:k for k,v in month_map.items()})
    grp = grp.sort_values("month_order")

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=grp["month_name"], y=grp["avg_popularity"], mode="lines+markers", name="Avg Popularity"))
    fig.add_trace(go.Scatter(x=grp["month_name"], y=grp["avg_score"], mode="lines+markers", name="Avg Netflix Score"))
    fig.update_layout(
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.85)"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    best_month = grp.sort_values("avg_score", ascending=False).head(1)["month_name"].iloc[0]
    info_card(
        "Actionable takeaway",
        f"""
Your filter window suggests a stronger release-month signal around
<b style="color:{NETFLIX_RED};">{best_month}</b> (by Avg Netflix Score).<br><br>
Use this as a portfolio narrative: “We test seasonal windows and validate with engagement signals.”
"""
    )


# -------------------- MARKET OPPORTUNITIES --------------------
def _explode_genres(df_use: pd.DataFrame, genre_map_in: dict) -> pd.DataFrame:
    inv = {v: k for k, v in genre_map_in.items()}
    rows = []
    for _, r in df_use.iterrows():
        gids = r.get("genre_ids") or []
        if not gids:
            rows.append({**r.to_dict(), "genre": "Unknown"})
        else:
            for gid in gids:
                rows.append({**r.to_dict(), "genre": inv.get(gid, "Unknown")})
    return pd.DataFrame(rows)

def _genre_agg(df_use: pd.DataFrame, genre_map_in: dict) -> pd.DataFrame:
    ex = _explode_genres(df_use, genre_map_in)
    g = ex.groupby("genre", as_index=False).agg(
        titles=("id", "count"),
        avg_rating=("vote_average", "mean"),
        avg_popularity=("popularity", "mean"),
        avg_score=("netflix_score", "mean"),
        total_votes=("vote_count", "sum"),
        avg_engagement=("engagement", "mean"),
    )
    g["z_titles"] = zscore(g["titles"])
    g["z_score"] = zscore(g["avg_score"])
    g["z_popularity"] = zscore(g["avg_popularity"])
    g["z_rating"] = zscore(g["avg_rating"])
    g["z_votes"] = zscore(np.log1p(g["total_votes"]))
    return g.sort_values("titles", ascending=False).reset_index(drop=True)

def page_market_opportunities(df_use: pd.DataFrame):
    st.markdown("## 🎯 Market Opportunity Intelligence")
    st.caption("Identify white-space: underserved demand pockets vs oversaturated genres — with an explainable scoring engine.")

    c1, c2, c3, c4 = st.columns([0.28, 0.24, 0.24, 0.24])
    with c1:
        min_titles = st.slider("Minimum titles per genre (avoid noise)", 1, 20, 4, 1)
    with c2:
        perf_axis = st.selectbox("Performance axis", ["Avg Netflix Score", "Avg Popularity", "Avg Rating"], index=0)
    with c3:
        vol_axis = st.selectbox("Volume axis", ["# Titles", "Total Votes (log)"], index=0)
    with c4:
        score_style = st.selectbox("Opportunity style", ["Balanced", "Quality-first", "Reach-first"], index=0)

    st.markdown("---")

    g = _genre_agg(df_use, genre_map)
    g2 = g[g["titles"] >= min_titles].copy()
    if g2.empty:
        st.warning("No genres meet your minimum-title threshold. Lower the slider.")
        return

    if perf_axis == "Avg Popularity":
        g2["perf"] = g2["avg_popularity"]; g2["z_perf"] = g2["z_popularity"]; perf_label = "Avg Popularity (Reach)"
    elif perf_axis == "Avg Rating":
        g2["perf"] = g2["avg_rating"]; g2["z_perf"] = g2["z_rating"]; perf_label = "Avg Rating (Quality)"
    else:
        g2["perf"] = g2["avg_score"]; g2["z_perf"] = g2["z_score"]; perf_label = "Avg Netflix Score (Composite)"

    if vol_axis == "Total Votes (log)":
        g2["volume"] = np.log1p(g2["total_votes"]); g2["z_volume"] = zscore(g2["volume"]); vol_label = "Total Votes (log)"
    else:
        g2["volume"] = g2["titles"]; g2["z_volume"] = g2["z_titles"]; vol_label = "Market Volume (# Titles)"

    if score_style == "Quality-first":
        g2["opp_score"] = (1.10 * g2["z_rating"]) + (0.70 * g2["z_perf"]) - (1.00 * g2["z_volume"]) + (0.25 * g2["z_votes"])
    elif score_style == "Reach-first":
        g2["opp_score"] = (1.10 * g2["z_popularity"]) + (0.70 * g2["z_perf"]) - (1.00 * g2["z_volume"]) + (0.25 * g2["z_votes"])
    else:
        g2["opp_score"] = (0.80 * g2["z_perf"]) + (0.55 * g2["z_rating"]) + (0.55 * g2["z_popularity"]) - (1.10 * g2["z_volume"]) + (0.15 * g2["z_votes"])

    perf_med = g2["perf"].median()
    vol_med = g2["volume"].median()

    def zone(row):
        high_perf = row["perf"] >= perf_med
        high_vol = row["volume"] >= vol_med
        if high_perf and not high_vol:
            return "Opportunity"
        if (not high_perf) and high_vol:
            return "Oversaturated"
        if high_perf and high_vol:
            return "Hit Factory"
        return "Niche / Experimental"

    g2["zone"] = g2.apply(zone, axis=1)

    best = g2.sort_values("opp_score", ascending=False).head(1)
    top_genre = best["genre"].iloc[0]
    top_score = best["opp_score"].iloc[0]
    underserved = int((g2["zone"] == "Opportunity").sum())
    oversat = int((g2["zone"] == "Oversaturated").sum())

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("TOP OPPORTUNITY", top_genre, "Best white-space candidate")
    with k2:
        metric_card("OPPORTUNITY SCORE", f"{top_score:.2f}", f"Style: {score_style}")
    with k3:
        metric_card("OPPORTUNITY ZONES", f"{underserved}", "High perf + low volume")
    with k4:
        metric_card("OVERSATURATED ZONES", f"{oversat}", "High volume + low perf")

    st.markdown("---")

    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("### 🧭 Market Map (White Space Quadrants)")
        st.caption("Top-left = white space. Bubble size = Opportunity Score strength.")

        plot = g2.copy()
        plot["size"] = (plot["opp_score"] - plot["opp_score"].min() + 1.6).clip(lower=1.6)

        fig = px.scatter(
            plot,
            x="volume",
            y="perf",
            size="size",
            color="zone",
            hover_data={"genre": True, "titles": True, "avg_rating":":.2f", "avg_popularity":":.2f", "avg_score":":.2f", "opp_score":":.2f"},
            text="genre",
        )
        fig.update_traces(textposition="top center", textfont=dict(size=11, color="rgba(255,255,255,0.75)"))
        fig.update_layout(
            height=520,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(title=vol_label, gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(title=perf_label, gridcolor="rgba(255,255,255,0.08)")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### 🧠 Strategy Intel")
        b = best.iloc[0]
        memo = f"""
<b style="color:{NETFLIX_RED};">Why {html.escape(b['genre'])} now?</b><br>
<ul style="margin:8px 0 0 0; padding-left:18px;">
  <li>Performance above median on <i>{html.escape(perf_axis)}</i> (signal: <b>{b['perf']:.2f}</b>)</li>
  <li>Competition below median on <i>{html.escape(vol_axis)}</i> (signal: <b>{b['volume']:.2f}</b>)</li>
  <li>Zone: <b style="color:{NETFLIX_RED};">{html.escape(b['zone'])}</b> — “white space” pocket</li>
</ul>
<b>Next moves</b><br>
<ol style="margin:8px 0 0 0; padding-left:18px;">
  <li>Greenlight 1–2 pilots with a differentiated hook (sub-genre + theme + talent).</li>
  <li>Launch with engagement-first tactics (trailer A/B, creator cuts) to convert votes into reach.</li>
  <li>Validate with: votes velocity + popularity lift + rating stability (first 7–14 days).</li>
</ol>
"""
        info_card("Investment Memo (Auto)", memo)

    st.markdown("---")
    st.markdown("### 🏆 Ranked Opportunities")
    st.caption("Sorted by Opportunity Score (higher = stronger white-space case).")

    g_rank = g2.sort_values("opp_score", ascending=False).reset_index(drop=True)
    show_cols = ["genre", "zone", "titles", "avg_rating", "avg_popularity", "avg_score", "opp_score"]
    st.dataframe(
        g_rank[show_cols].style.format({
            "avg_rating": "{:.2f}",
            "avg_popularity": "{:.2f}",
            "avg_score": "{:.2f}",
            "opp_score": "{:.2f}",
        }),
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.markdown("### 🎬 Genre Drilldown")
    pick_genre = st.selectbox("Pick a genre to drill in", g_rank["genre"].tolist(), index=0)

    ex = _explode_genres(df_use, genre_map)
    gdf = ex[ex["genre"] == pick_genre].copy()
    if gdf.empty:
        st.info("No titles for this genre in the current filter window.")
        return

    d1, d2 = st.columns([1.0, 1.0], gap="large")
    with d1:
        st.markdown("#### ⭐ Best bets (High Netflix Score)")
        top_titles = gdf.sort_values("netflix_score", ascending=False).head(8)
        cols = st.columns(4)
        for i, (_, row) in enumerate(top_titles.iterrows()):
            with cols[i % 4]:
                if row["poster_url"]:
                    tmdb_url = f"https://www.themoviedb.org/movie/{int(row['id'])}"
                    clickable_poster(row["poster_url"], tmdb_url, alt=row["title"], height_px=240)
                st.caption(f"**{row['title']}**")
                st.caption(f"⭐ {row['vote_average']:.1f} · 🔥 {row['netflix_score']:.2f}")

    with d2:
        st.markdown("#### 🕵️ Underdog gems (High rating, lower popularity)")
        med_pop = gdf["popularity"].median()
        gems = gdf[(gdf["vote_average"] >= gdf["vote_average"].quantile(0.70)) & (gdf["popularity"] <= med_pop)]
        gems = gems.sort_values(["vote_average", "netflix_score"], ascending=False).head(8)
        if gems.empty:
            st.info("No underdog gems found for this genre in the current window.")
        else:
            cols = st.columns(4)
            for i, (_, row) in enumerate(gems.iterrows()):
                with cols[i % 4]:
                    if row["poster_url"]:
                        tmdb_url = f"https://www.themoviedb.org/movie/{int(row['id'])}"
                        clickable_poster(row["poster_url"], tmdb_url, alt=row["title"], height_px=240)
                    st.caption(f"**{row['title']}**")
                    st.caption(f"⭐ {row['vote_average']:.1f} · 👀 {row['popularity']:.1f}")


# -------------------- RECOMMENDATION COPILOT --------------------
def page_recommendation_copilot(df_use: pd.DataFrame):
    st.markdown("## 💡 Recommendation & Risk Copilot")
    st.caption("Interactive investment simulator: test scenarios (genre + budget + timing) and get data-driven recommendations.")

    info_card(
        "Business Problem",
        "Should we invest in this content profile? This tool estimates performance from <b>genre</b>, <b>budget</b>, and <b>release timing</b>, "
        "surfaces <b>risk</b>, and shows <b>similar winners</b> to validate decisions before committing resources."
    )

    st.markdown("### 📝 Content Profile Configuration")
    cfg1, cfg2, cfg3, cfg4 = st.columns([0.35, 0.22, 0.22, 0.21])

    with cfg1:
        copilot_genre = st.selectbox(
            "Genre",
            ["Use sidebar filters"] + [g for g in sorted(genre_map.keys())],
            index=0,
        )

    with cfg2:
        content_type = st.radio("Type", ["Movie", "TV Show"], index=0, horizontal=True)

    with cfg3:
        budget = st.slider("Budget level", 1, 10, 7, 1)

    with cfg4:
        release_q = st.selectbox("Release quarter", ["Q1 (Jan–Mar)", "Q2 (Apr–Jun)", "Q3 (Jul–Sep)", "Q4 (Oct–Dec)"], index=0)

    if copilot_genre == "Use sidebar filters" or copilot_genre not in genre_map:
        d = df_use.copy()
        genre_label = selected_genre if selected_genre != "All" else "All (Filtered)"
    else:
        gid = genre_map[copilot_genre]
        d = df_use[df_use["genre_ids"].apply(lambda ids: gid in (ids or []))].copy()
        genre_label = copilot_genre

    if d.empty:
        st.warning("No titles found for this Copilot genre within your current sidebar filters.")
        return

    q_to_months = {
        "Q1 (Jan–Mar)": [1, 2, 3],
        "Q2 (Apr–Jun)": [4, 5, 6],
        "Q3 (Jul–Sep)": [7, 8, 9],
        "Q4 (Oct–Dec)": [10, 11, 12],
    }

    base_all = df_use.copy()
    base_all_pop = base_all["popularity"].mean()
    base_all_rating = base_all["vote_average"].mean()
    base_all_score = base_all["netflix_score"].mean()

    g_avg_pop = d["popularity"].mean()
    g_avg_rating = d["vote_average"].mean()
    g_avg_score = d["netflix_score"].mean()
    g_titles = int(len(d))

    b = math.log1p(budget) / math.log1p(10)

    months = q_to_months[release_q]
    d_q = d[d["release_month"].isin(months)].copy()
    if len(d_q) >= 3:
        q_pop = d_q["popularity"].mean()
        timing_lift = (q_pop - g_avg_pop) / (g_avg_pop + 1e-6)
    else:
        timing_lift = 0.0
    timing_lift = max(-0.25, min(0.25, timing_lift))

    rel_pop = (g_avg_pop - base_all_pop) / (base_all_pop + 1e-6)
    rel_rating = (g_avg_rating - base_all_rating) / (base_all_rating + 1e-6)
    rel_score = (g_avg_score - base_all_score) / (base_all_score + 1e-6)

    raw = 0.50 * rel_pop + 0.30 * rel_score + 0.20 * rel_rating
    raw += 0.55 * (b - 0.5)
    raw += 0.60 * timing_lift

    pred_0_1 = clamp01(0.50 + raw)
    pred_popularity = int(round(1 + pred_0_1 * 9))

    hit_prob = sigmoid((pred_popularity - 5.0) / 1.25)
    hit_pct = 100.0 * hit_prob

    risk_level = "Low"
    risk_cls = "low"
    if g_titles < 10 or g_avg_rating < base_all_rating - 0.2:
        risk_level = "Medium"; risk_cls = "med"
    if g_titles < 6 or g_avg_rating < base_all_rating - 0.6:
        risk_level = "High"; risk_cls = "high"

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("PREDICTED POPULARITY", f"{pred_popularity}", f"Profile: {genre_label} • {content_type}")
    with k2:
        metric_card("HIT PROBABILITY", f"{hit_pct:.1f}%", "Chance of Top-quartile outcome")
    with k3:
        info_card("RISK LEVEL", f"{pill(risk_level, risk_cls)}<br><span style='color:{MUTED};'>Based on sample size + genre quality.</span>")
    with k4:
        metric_card("GENRE AVG RATING", f"{g_avg_rating:.1f}/10", f"{g_titles} titles in window")

    st.markdown("---")

    left, right = st.columns([1.05, 0.95], gap="large")

    with left:
        st.markdown("### 📈 Budget Impact Forecast")
        st.caption("Diminishing returns curve + your selected budget marked as the decision point.")

        xs = list(range(1, 11))
        ys = []
        for bb in xs:
            bbb = math.log1p(bb) / math.log1p(10)
            raw_b = (0.50 * rel_pop + 0.30 * rel_score + 0.20 * rel_rating) + 0.55 * (bbb - 0.5) + 0.60 * timing_lift
            pred_b = clamp01(0.50 + raw_b)
            ys.append(1 + pred_b * 9)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines+markers", name="Predicted Popularity"))
        fig.add_trace(go.Scatter(x=[budget], y=[ys[budget-1]], mode="markers", name="Your Selection",
                                 marker=dict(symbol="star", size=16)))
        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )
        fig.update_xaxes(title="Budget level (1–10)", gridcolor="rgba(255,255,255,0.08)")
        fig.update_yaxes(title="Predicted Popularity (1–10)", gridcolor="rgba(255,255,255,0.08)", range=[1, 10.2])
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown("### 🧬 Content DNA Profile (Radar)")
        st.caption("A quick profile across reach, quality, engagement, scale, votes, and recency.")

        all_pop = base_all["popularity"]
        all_rating = base_all["vote_average"]
        all_eng = base_all["engagement"]
        all_votes = np.log1p(base_all["vote_count"])
        all_year = base_all["release_year_num"].fillna(base_all["release_year_num"].median())

        g_pop = g_avg_pop
        g_qual = g_avg_rating
        g_eng = d["engagement"].mean()
        g_votes = float(np.log1p(d["vote_count"]).mean())
        g_rec = float(d["release_year_num"].fillna(all_year.median()).median())
        g_vol = float(len(d))

        pop_n = norm_0_100(g_pop, float(all_pop.min()), float(all_pop.max()))
        qual_n = norm_0_100(g_qual, float(all_rating.min()), float(all_rating.max()))
        eng_n = norm_0_100(g_eng, float(all_eng.min()), float(all_eng.max()))
        votes_n = norm_0_100(g_votes, float(all_votes.min()), float(all_votes.max()))
        rec_n = norm_0_100(g_rec, float(all_year.min()), float(all_year.max()))
        vol_n = norm_0_100(g_vol, 1.0, float(max(2.0, base_all.shape[0])))

        cats = ["Popularity", "Quality", "Engagement", "Market Volume", "Vote Strength", "Recency"]
        vals = [pop_n, qual_n, eng_n, vol_n, votes_n, rec_n]

        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(r=vals + [vals[0]], theta=cats + [cats[0]], fill="toself", name="Profile"))
        fig.update_layout(
            height=420,
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(color="rgba(255,255,255,0.85)"),
            margin=dict(l=20, r=20, t=20, b=20),
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0, 100], gridcolor="rgba(255,255,255,0.10)"),
                angularaxis=dict(gridcolor="rgba(255,255,255,0.10)"),
            ),
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    cA, cB = st.columns([1, 1], gap="large")
    with cA:
        peak_budget = int(np.argmax(ys) + 1)
        body = (
            f"Your budget <b style='color:{NETFLIX_RED};'>{budget}/10</b> predicts <b style='color:{NETFLIX_RED};'>{pred_popularity}</b> popularity.<br>"
            f"Peak on the curve occurs around <b style='color:{NETFLIX_RED};'>{peak_budget}/10</b> (~{ys[peak_budget-1]:.1f}).<br>"
            "Returns slow down at the top: choose a level where marginal gain justifies spend."
        )
        info_card("Investment ROI Curve", body)

    with cB:
        strongest = cats[int(np.argmax(vals))]
        weakest = cats[int(np.argmin(vals))]
        body = (
            f"Strongest dimension: {pill(strongest, 'low')} — leverage as a positioning pillar.<br><br>"
            f"Weakest dimension: {pill(weakest, 'high')} — mitigate with packaging (creative, casting, marketing).<br><br>"
            "Balanced shapes = versatile genres; spiky shapes need strategy to offset weak sides."
        )
        info_card("Multi-Dimensional Profile Analysis", body)

    st.markdown("---")

    st.markdown("### 🎬 Similar High-Performing Titles — Study These")
    st.caption("Top titles in this profile (within your current filter window). Click posters to open TMDB.")

    sim = d.sort_values(["popularity", "netflix_score"], ascending=False).head(12).reset_index(drop=True)
    cols = st.columns(6)
    for i, row in sim.iterrows():
        with cols[i % 6]:
            if row["poster_url"]:
                tmdb_url = f"https://www.themoviedb.org/movie/{int(row['id'])}"
                clickable_poster(row["poster_url"], tmdb_url, alt=row["title"], height_px=220)
            st.caption(f"{row['title']}")
            st.caption(f"⭐ {row['vote_average']:.1f} · 🔥 {row['netflix_score']:.1f}")

    st.markdown("---")

    decision = "PROCEED with confidence" if risk_level == "Low" and hit_pct >= 60 else ("PROCEED with caution" if risk_level != "High" else "HOLD / REWORK")

    rec_html = f"""
<div style="display:flex; flex-direction:column; gap:10px;">
  <div style="font-weight:900; font-size:18px;">📊 ML-Powered Investment Recommendation</div>
  <div style="color:{MUTED};">Profile: <b>{html.escape(genre_label)}</b> {html.escape(content_type)}, Budget {budget}/10, {html.escape(release_q)}</div>
  <div>Predicted Performance: <b style="color:{NETFLIX_RED};">{pred_popularity}</b> popularity score</div>
  <div>Success Probability: <b style="color:{NETFLIX_RED};">{hit_pct:.1f}%</b> chance of top-quartile outcome</div>
  <div>Risk Level: {pill(risk_level, risk_cls)}</div>
  <hr style="border-color: rgba(255,255,255,0.10); margin: 8px 0;">
  <div>Decision:
    <span class="pill pill-med"
      style="background: rgba(229,9,20,0.18); border-color: rgba(229,9,20,0.35); color: rgba(255,255,255,0.92); font-size: 13px;">
      {html.escape(decision)}
    </span>
  </div>
</div>
"""
    info_card(" ", rec_html)


# -------------------- PREDICTIVE FORECASTING (UPGRADED) --------------------
def page_predictive_forecasting(df_use: pd.DataFrame):
    st.markdown("## 🔮 Predictive Forecasting & Trend Intelligence")
    st.caption("Forecast emerging patterns for the next 6–12 months using live TMDB signals (explainable + demo-friendly).")

    info_card(
        "Business Problem",
        "What will demand look like in the next <b>6–12 months</b>? This page forecasts <b>genre engagement trend</b>, "
        "estimates <b>lifecycle decay</b>, and highlights <b>rising stars</b> so you can plan pipeline and investments."
    )

    ex_all = _explode_genres_movies(df_use, genre_map)
    ex_all = ex_all.dropna(subset=["release_year_num"]).copy()

    c1, c2, c3, c4 = st.columns([0.40, 0.20, 0.20, 0.20])
    with c1:
        avail = sorted([g for g in ex_all["genre"].dropna().unique().tolist() if g != "Unknown"])
        default_pick = avail[:6] if len(avail) >= 6 else avail
        pick_genres = st.multiselect("Genres to forecast (lines)", options=avail, default=default_pick)
    with c2:
        horizon = st.slider("Forecast horizon (months)", 6, 12, 12, 1)
    with c3:
        hist_years = st.slider("History window (years)", 5, 15, 12, 1)
    with c4:
        band_strength = st.selectbox("Confidence band", ["Narrow (±0.6σ)", "Standard (±1.0σ)", "Wide (±1.6σ)"], index=1)

    if not pick_genres:
        st.info("Pick at least one genre to generate the forecast.")
        return

    if ex_all.empty:
        st.warning("Not enough release-year data in the current filtered window to forecast.")
        return

    band_k = {"Narrow (±0.6σ)": 0.6, "Standard (±1.0σ)": 1.0, "Wide (±1.6σ)": 1.6}[band_strength]

    max_y = int(ex_all["release_year_num"].max())
    min_y = max(int(ex_all["release_year_num"].min()), max_y - hist_years)
    hist = ex_all[(ex_all["release_year_num"] >= min_y) & (ex_all["release_year_num"] <= max_y)].copy()
    if hist.empty:
        st.warning("Not enough historical points after trimming to your selected history window.")
        return

    g_year = hist.groupby(["genre", "release_year_num"], as_index=False).agg(
        avg_eng=("engagement", "mean"),
        titles=("id", "count"),
        avg_pop=("popularity", "mean"),
        avg_score=("netflix_score", "mean"),
        avg_votes=("vote_count", "mean"),
    )

    months_ahead = np.arange(1, horizon + 1)

    st.markdown("---")
    st.markdown("### 📈 Genre Engagement Forecast")
    st.caption("Trend model fits engagement vs time (release year) and projects forward; bands reflect uncertainty from residuals.")

    fig = go.Figure()
    intel_rows = []

    for g in pick_genres:
        gg = g_year[g_year["genre"] == g].copy()
        if gg.empty or gg["release_year_num"].nunique() < 3:
            continue

        x = gg["release_year_num"].to_numpy(dtype=float)
        y = gg["avg_eng"].to_numpy(dtype=float)

        x_last = float(np.nanmax(x))
        x_future = x_last + (months_ahead / 12.0)

        yhat, sigma = _robust_lin_forecast(x, y, x_future)
        lo = yhat - band_k * sigma
        hi = yhat + band_k * sigma

        fig.add_trace(go.Scatter(
            x=months_ahead,
            y=yhat,
            mode="lines+markers",
            name=g,
            hovertemplate="Month %{x}<br>Predicted Engagement %{y:.2f}<extra></extra>"
        ))

        fig.add_trace(go.Scatter(
            x=np.concatenate([months_ahead, months_ahead[::-1]]),
            y=np.concatenate([hi, lo[::-1]]),
            fill="toself",
            name=f"{g} band",
            hoverinfo="skip",
            showlegend=False,
            opacity=0.18,
            line=dict(width=0),
        ))

        y0 = float(yhat[0]) if len(yhat) else 0.0
        yN = float(yhat[-1]) if len(yhat) else 0.0
        growth_pct = 0.0 if abs(y0) < 1e-9 else (100.0 * (yN - y0) / abs(y0))
        slope = float(np.polyfit(x, y, 1)[0]) if len(x) >= 2 else 0.0

        intel_rows.append({
            "Genre": g,
            "Forecast Growth %": growth_pct,
            "Momentum (slope)": slope,
            "Hist Years": int(gg["release_year_num"].nunique()),
            "Titles (hist)": int(gg["titles"].sum()),
        })

    fig.update_layout(
        height=520,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.85)"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    fig.update_xaxes(title="Months Ahead", gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(title="Predicted Engagement (proxy)", gridcolor="rgba(255,255,255,0.08)")
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    left, right = st.columns([0.95, 1.05], gap="large")

    with left:
        st.markdown("### 🧠 ML Forecast Intelligence")
        if intel_rows:
            intel = pd.DataFrame(intel_rows)
            intel["Momentum (slope)"] = pd.to_numeric(intel["Momentum (slope)"], errors="coerce")
            intel = intel.sort_values(["Forecast Growth %", "Momentum (slope)"], ascending=False)

            top = intel.head(1).iloc[0]
            growth = float(top["Forecast Growth %"])
            lvl = "low"
            if growth < 0:
                lvl = "high"
            elif growth < 10:
                lvl = "med"

            info_card(
                "Forecast Summary",
                f"""
{pill(str(top['Genre']), 'med')} shows strongest {horizon}-month forecast trajectory
(<b style="color:{NETFLIX_RED};">{growth:+.1f}%</b>).<br><br>
<ul style="margin:0; padding-left:18px;">
  <li>Upward slopes = growth opportunity</li>
  <li>Flat/declining = wait, reposition, or reduce bet size</li>
</ul>
<div style="margin-top:10px; color:{MUTED};">Tip: Use this to narrate “pipeline planning” and “greenlight timing”.</div>
"""
            )

            st.dataframe(
                intel.style.format({
                    "Forecast Growth %": "{:+.1f}",
                    "Momentum (slope)": "{:+.4f}",
                }),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("Not enough history points for the selected genres. Try widening the year range or selecting other genres.")

    with right:
        st.markdown("### ⏳ Lifecycle & Decay Signals")
        st.caption("A simple lifecycle curve: older titles usually lose engagement. We estimate decay to guide refresh strategy.")

        d = df_use.dropna(subset=["release_year_num"]).copy()
        d["age"] = (d["release_year_num"].max() - d["release_year_num"]).clip(lower=0)
        if len(d) < 8:
            st.info("Not enough data to model lifecycle.")
        else:
            x = d["age"].to_numpy(dtype=float)
            y = np.log1p(d["engagement"].to_numpy(dtype=float))
            a, b = np.polyfit(x, y, 1)
            decay_per_year = float(a)

            x_grid = np.linspace(float(np.min(x)), float(np.max(x)), 40)
            yhat = a * x_grid + b
            yhat_lin = np.expm1(yhat)

            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=d["age"],
                y=d["engagement"],
                mode="markers",
                name="Titles",
                hovertemplate="Age %{x:.0f}y<br>Engagement %{y:.2f}<extra></extra>"
            ))
            fig2.add_trace(go.Scatter(
                x=x_grid,
                y=yhat_lin,
                mode="lines",
                name="Lifecycle fit",
            ))
            fig2.update_layout(
                height=430,
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="rgba(255,255,255,0.85)"),
                margin=dict(l=10, r=10, t=10, b=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            )
            fig2.update_xaxes(title="Age (years since latest year in window)", gridcolor="rgba(255,255,255,0.08)")
            fig2.update_yaxes(title="Engagement (proxy)", gridcolor="rgba(255,255,255,0.08)")
            st.plotly_chart(fig2, use_container_width=True)

            cls = "low" if decay_per_year >= -0.02 else ("med" if decay_per_year >= -0.06 else "high")
            info_card(
                "Decay Interpretation",
                f"""
Estimated decay slope (log scale): <b style="color:{NETFLIX_RED};">{decay_per_year:+.4f}</b> per year.<br><br>
{pill("Stable lifecycle" if cls=="low" else ("Moderate decay" if cls=="med" else "Fast decay"), cls)}<br><br>
<span style="color:{MUTED};">Use this to justify refresh cycles, sequels, re-marketing, or catalog rotation.</span>
"""
            )

    st.markdown("---")
    st.markdown("### ⭐ Rising Stars — Fastest Growing Titles (Velocity)")
    st.caption("Velocity = popularity per day since release (simple, explainable, and looks great in a demo).")

    d = df_use.copy()
    d["release_dt"] = pd.to_datetime(d["release_date"], errors="coerce")
    d = d.dropna(subset=["release_dt"]).copy()
    if d.empty:
        st.info("No release dates available to compute velocity.")
        return

    now_year = int(df_use["release_year_num"].dropna().max()) if df_use["release_year_num"].dropna().size else 2025
    d = d[d["release_dt"].dt.year >= max(2000, now_year - 3)].copy()

    if d.empty:
        st.info("No recent titles (last ~3 years of your filter window) for velocity analysis.")
        return

    today = pd.Timestamp.now(tz=None)
    d["days_since_release"] = (today - d["release_dt"]).dt.days.clip(lower=1)
    d["velocity"] = d["popularity"] / d["days_since_release"]

    genre_filter = st.selectbox("Optional: focus Rising Stars by genre", ["All"] + sorted([g for g in ex_all["genre"].unique().tolist() if g != "Unknown"]), index=0)
    if genre_filter != "All":
        ex = _explode_genres_movies(d, genre_map)
        d = ex[ex["genre"] == genre_filter].copy()

    if d.empty:
        st.info("No titles in that Rising Stars slice.")
        return

    stars = d.sort_values(["velocity", "popularity", "netflix_score"], ascending=False).head(12).reset_index(drop=True)

    k1, k2, k3 = st.columns(3)
    with k1:
        metric_card("TOP VELOCITY", f"{stars['velocity'].max():.4f}", "Popularity per day")
    with k2:
        metric_card("TOP POPULARITY", f"{stars['popularity'].max():.1f}", "Reach signal")
    with k3:
        metric_card("TOP SCORE", f"{stars['netflix_score'].max():.1f}", "Composite")

    cols = st.columns(6)
    for i, row in stars.iterrows():
        with cols[i % 6]:
            if row.get("poster_url"):
                tmdb_url = f"https://www.themoviedb.org/movie/{int(row['id'])}"
                clickable_poster(row["poster_url"], tmdb_url, alt=row.get("title", ""), height_px=210)
            st.caption(f"**{row.get('title','')}**")
            st.caption(f"⚡ {row['velocity']:.4f} · 🔥 {row['netflix_score']:.1f} · ⭐ {row['vote_average']:.1f}")


# -------------------- HEAD-TO-HEAD COMPARISON (UPGRADED) --------------------
def page_head_to_head(df_use: pd.DataFrame):
    st.markdown("## ⚖️ Head-to-Head Comparison Engine")
    st.caption("Compare two genres or two titles side-by-side across key metrics with an auto-calculated winner.")

    info_card(
        "Business Problem",
        "Should we choose <b>Genre A</b> or <b>Genre B</b>? Or invest in <b>Title X</b> vs <b>Title Y</b>? "
        "This engine provides a direct metric-by-metric comparison + a clear winner for fast decisions."
    )

    mode = st.radio("Comparison Mode", ["Genre vs Genre", "Title vs Title"], index=0, horizontal=True)

    st.markdown("---")

    def genre_slice(name: str) -> pd.DataFrame:
        if name == "All (Filtered)":
            return df_use.copy()
        gid = genre_map.get(name)
        if gid is None:
            return pd.DataFrame()
        return df_use[df_use["genre_ids"].apply(lambda ids: gid in (ids or []))].copy()

    def title_slice(title: str) -> pd.DataFrame:
        return df_use[df_use["title"] == title].copy()

    if mode == "Genre vs Genre":
        options = ["All (Filtered)"] + sorted(genre_map.keys())
        c1, c2 = st.columns(2)
        with c1:
            A = st.selectbox("Select Genre A", options, index=1 if len(options) > 1 else 0)
        with c2:
            B = st.selectbox("Select Genre B", options, index=2 if len(options) > 2 else 0)

        dA = genre_slice(A)
        dB = genre_slice(B)

        if dA.empty or dB.empty:
            st.warning("One of the selected slices has no titles in the current filter window.")
            return

        total_titles = float(len(df_use))
        def metrics(d: pd.DataFrame):
            return {
                "Avg Popularity": float(d["popularity"].mean()),
                "Avg Rating": float(d["vote_average"].mean()),
                "Total Titles": float(len(d)),
                "Avg Votes": float(d["vote_count"].mean()),
                "Avg Engagement": float(d["engagement"].mean()),
                "Market Share %": float(100.0 * len(d) / max(1.0, total_titles)),
                "Opportunity Score": float(_opportunity_score_for_slice(d)),
            }

        mA = metrics(dA)
        mB = metrics(dB)

        labelA = A
        labelB = B

    else:
        titles = df_use.sort_values("netflix_score", ascending=False)["title"].dropna().unique().tolist()
        if len(titles) < 2:
            st.warning("Not enough titles in this window to compare.")
            return

        c1, c2 = st.columns(2)
        with c1:
            A = st.selectbox("Select Title A", titles, index=0)
        with c2:
            B = st.selectbox("Select Title B", titles, index=1)

        dA = title_slice(A)
        dB = title_slice(B)

        if dA.empty or dB.empty:
            st.warning("One of the selected titles is missing in the current filter window.")
            return

        rowA = dA.iloc[0]
        rowB = dB.iloc[0]

        def metrics_row(r: pd.Series):
            return {
                "Popularity": float(r["popularity"]),
                "Rating": float(r["vote_average"]),
                "Votes": float(r["vote_count"]),
                "Netflix Score": float(r["netflix_score"]),
                "Engagement": float(r["engagement"]),
                "Release Year": float(r["release_year_num"]) if pd.notna(r["release_year_num"]) else np.nan,
                "Recency (newer=better)": float(r["release_year_num"]) if pd.notna(r["release_year_num"]) else np.nan,
            }

        mA = metrics_row(rowA)
        mB = metrics_row(rowB)

        labelA = A
        labelB = B

    headline = "Opportunity Score" if mode == "Genre vs Genre" else "Netflix Score"
    A_val = mA[headline]
    B_val = mB[headline]

    win_head = "A" if A_val >= B_val else "B"
    win_label = labelA if win_head == "A" else labelB

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        metric_card("WINNER (HEADLINE)", win_label[:16] + ("…" if len(win_label) > 16 else ""), f"Based on {headline}")
    with k2:
        metric_card("A • HEADLINE", f"{A_val:.2f}", labelA[:22] + ("…" if len(labelA) > 22 else ""))
    with k3:
        metric_card("B • HEADLINE", f"{B_val:.2f}", labelB[:22] + ("…" if len(labelB) > 22 else ""))
    with k4:
        metric_card("DECISION CONFIDENCE", "High" if abs(A_val - B_val) / (abs(A_val) + abs(B_val) + 1e-6) > 0.08 else "Medium",
                    "Larger gaps = clearer choice")

    st.markdown("---")
    st.markdown("### 📋 Side-by-Side Metrics Comparison")
    st.caption("Winner is computed row-by-row (higher is better).")

    rows = []
    win_count_A = 0
    win_count_B = 0

    for metric, a in mA.items():
        b = mB.get(metric, np.nan)
        higher_better = True
        if metric == "Recency (newer=better)":
            higher_better = True

        w = _winner(a, b, higher_is_better=higher_better)
        if w == "A":
            win_count_A += 1
        elif w == "B":
            win_count_B += 1

        rows.append({
            "Metric": metric,
            "A": a,
            "B": b,
            "Winner": labelA if w == "A" else (labelB if w == "B" else "—")
        })

    comp = pd.DataFrame(rows)
    fmt = comp.copy()
    for col in ["A", "B"]:
        fmt[col] = pd.to_numeric(fmt[col], errors="coerce")

    st.dataframe(
        fmt.style.format({"A": "{:.4g}", "B": "{:.4g}"}),
        use_container_width=True,
        hide_index=True
    )

    winner_text = labelA if win_count_A >= win_count_B else labelB
    winner_count = max(win_count_A, win_count_B)

    st.markdown(
        f"""
        <div class="nx-card" style="border-radius:16px; border:1px solid rgba(229,9,20,0.22); background: rgba(229,9,20,0.14);">
          <div style="font-weight:900; font-size:16px;">🏆 WINNER: {html.escape(winner_text)} ({winner_count}/{len(rows)} metrics)</div>
          <div style="margin-top:6px; color:{MUTED};">Use this for quick decision-making when time is critical.</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.markdown("### 📊 Performance Comparison — Diverging Bars")
    st.caption("Bars extend from center: LEFT (red) = A, RIGHT (blue) = B. Longer bars = stronger performance on that metric.")

    show_metrics = [r["Metric"] for r in rows][:7]
    xA = []
    xB = []
    ycats = []

    for metric in show_metrics:
        a = float(mA.get(metric, np.nan))
        b = float(mB.get(metric, np.nan))
        denom = (abs(a) + abs(b) + 1e-6)
        pct = 100.0 * (a - b) / denom
        xA.append(-max(0.0, pct))
        xB.append(max(0.0, -pct))
        ycats.append(metric)

    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=ycats,
        x=xA,
        orientation="h",
        name=labelA,
        marker_color="rgba(229,9,20,0.85)",
        text=[f"{abs(v):.1f}" if v != 0 else "" for v in xA],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>A advantage: %{x:.1f}<extra></extra>"
    ))
    fig.add_trace(go.Bar(
        y=ycats,
        x=xB,
        orientation="h",
        name=labelB,
        marker_color="rgba(59,130,246,0.85)",
        text=[f"{abs(v):.1f}" if v != 0 else "" for v in xB],
        textposition="inside",
        insidetextanchor="middle",
        hovertemplate="%{y}<br>B advantage: %{x:.1f}<extra></extra>"
    ))
    fig.update_layout(
        height=420,
        barmode="overlay",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.85)"),
        margin=dict(l=10, r=10, t=10, b=10),
        xaxis=dict(title="Relative Advantage (scaled)", gridcolor="rgba(255,255,255,0.08)", zeroline=True, zerolinecolor="rgba(255,255,255,0.22)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.08)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.markdown("### 📉 Performance Trend Comparison")
    st.caption("Historical engagement trend proxy (by release year). Rising lines = growing audience interest.")

    ex = _explode_genres_movies(df_use, genre_map).dropna(subset=["release_year_num"]).copy()
    if ex.empty:
        st.info("Not enough release-year data for trend chart.")
        return

    if mode == "Genre vs Genre":
        def trend_for_genre(name: str):
            if name == "All (Filtered)":
                g = df_use.dropna(subset=["release_year_num"]).groupby("release_year_num", as_index=False).agg(avg_eng=("engagement", "mean"))
                g["name"] = "All (Filtered)"
                return g
            g = ex[ex["genre"] == name].groupby("release_year_num", as_index=False).agg(avg_eng=("engagement", "mean"))
            g["name"] = name
            return g

        gA = trend_for_genre(labelA)
        gB = trend_for_genre(labelB)

    else:
        def primary_genre_name(row: pd.Series):
            gids = row.get("genre_ids") or []
            if not gids:
                return "Unknown"
            inv = _inv_genre_map(genre_map)
            return inv.get(gids[0], "Unknown")

        gnameA = primary_genre_name(df_use[df_use["title"] == labelA].iloc[0])
        gnameB = primary_genre_name(df_use[df_use["title"] == labelB].iloc[0])

        def trend_for_genre(name: str):
            g = ex[ex["genre"] == name].groupby("release_year_num", as_index=False).agg(avg_eng=("engagement", "mean"))
            g["name"] = name
            return g

        gA = trend_for_genre(gnameA)
        gB = trend_for_genre(gnameB)

    figt = go.Figure()
    if not gA.empty:
        figt.add_trace(go.Scatter(x=gA["release_year_num"], y=gA["avg_eng"], mode="lines+markers", name="A trend"))
    if not gB.empty:
        figt.add_trace(go.Scatter(x=gB["release_year_num"], y=gB["avg_eng"], mode="lines+markers", name="B trend"))
    figt.update_layout(
        height=420,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="rgba(255,255,255,0.85)"),
        margin=dict(l=10, r=10, t=10, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    figt.update_xaxes(title="Year", gridcolor="rgba(255,255,255,0.08)")
    figt.update_yaxes(title="Avg Engagement (proxy)", gridcolor="rgba(255,255,255,0.08)")
    st.plotly_chart(figt, use_container_width=True)

    st.markdown("---")
    cL, cR = st.columns([1, 1], gap="large")
    with cL:
        info_card(
            "Head-to-Head Visual Analysis",
            f"""
<b style="color:{NETFLIX_RED};">RED (left)</b> = A • <b style="color:rgba(59,130,246,0.95);">BLUE (right)</b> = B<br><br>
<ul style="margin:0; padding-left:18px;">
  <li>Longer bars = stronger performance on that metric</li>
  <li>Quick rule: if one side dominates multiple metrics, that’s your clear winner</li>
</ul>
"""
        )
    with cR:
        info_card(
            "Trend Analysis Insights",
            """
<ul style="margin:0; padding-left:18px;">
  <li>Upward slopes indicate growing engagement and market momentum over time</li>
  <li>Flat or declining trends suggest saturation or shifting audience preferences</li>
  <li>Compare slopes to identify which option has the stronger long-term trajectory</li>
</ul>
"""
        )


# -------------------- ROUTER --------------------
if page == "Content Universe":
    page_content_universe(browse_df)
elif page == "Performance Deep Dive":
    page_performance_deep_dive(browse_df)
elif page == "Market Opportunities":
    page_market_opportunities(browse_df)
elif page == "Recommendation Copilot":
    page_recommendation_copilot(browse_df)
elif page == "Predictive Forecasting":
    page_predictive_forecasting(browse_df)
else:
    page_head_to_head(browse_df)


with st.expander("🔍 Raw Preview (Filtered)"):
    st.dataframe(
        browse_df[["title", "release_date", "vote_average", "vote_count", "popularity", "netflix_score"]].head(50),
        use_container_width=True
    )