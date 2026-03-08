"""
app.py — CineMatch Streamlit Frontend
Run: streamlit run app.py
Requires: main.py + movies.csv in the same folder
"""

import streamlit as st
from main import build_pipeline, recommendor, get_trending, search_suggestions

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CineMatch",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME  —  noir-gold dark  /  parchment light
# ─────────────────────────────────────────────────────────────────────────────
DARK = dict(
    bg="#0d0d0d", surface="#161616", card="#1c1c1c",
    accent="#e8c547", accent2="#c9a227", accent_muted="rgba(232,197,71,0.12)",
    text="#f0ece0", sub="#8a8880", border="#2a2a2a", badge_text="#111111",
)
LIGHT = dict(
    bg="#f5f0e6", surface="#ece6d6", card="#ffffff",
    accent="#b07d1a", accent2="#8a600f", accent_muted="rgba(176,125,26,0.10)",
    text="#1a1710", sub="#6b6050", border="#d8ceb8", badge_text="#ffffff",
)


def css(t: dict) -> str:
    return f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Lora:ital,wght@0,400;0,500;1,400&display=swap');

:root {{
  --bg:{t["bg"]}; --surface:{t["surface"]}; --card:{t["card"]};
  --accent:{t["accent"]}; --accent2:{t["accent2"]}; --accent-m:{t["accent_muted"]};
  --text:{t["text"]}; --sub:{t["sub"]}; --border:{t["border"]}; --bt:{t["badge_text"]};
}}

/* ── reset ── */
.stApp        {{ background:var(--bg) !important; }}
.main .block-container {{ max-width:1420px; padding:1.8rem 2.5rem 3rem; }}
#MainMenu,footer,header {{ visibility:hidden; }}
.stDeployButton {{ display:none; }}
h1,h2,h3      {{ font-family:'Bebas Neue',sans-serif !important; color:var(--text) !important; letter-spacing:.04em; }}
p,div,span,label,li {{ font-family:'Lora',Georgia,serif !important; color:var(--text); }}

/* ── hero ── */
.hero         {{ margin-bottom:1.8rem; display:flex; align-items:baseline; gap:1rem; }}
.hero-logo    {{ font-family:'Bebas Neue',sans-serif; font-size:3.6rem; color:var(--text); line-height:1; }}
.hero-logo em {{ color:var(--accent); font-style:normal; }}
.hero-tagline {{ font-family:'Lora',serif; font-size:0.78rem; letter-spacing:0.28em;
                 text-transform:uppercase; color:var(--sub); }}

/* ── section headers ── */
.sec-eyebrow  {{ font-family:'Lora',serif; font-size:0.68rem; letter-spacing:0.3em;
                 text-transform:uppercase; color:var(--accent); margin-bottom:.25rem; }}
.sec-head     {{ font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--text);
                 border-bottom:1px solid var(--border); padding-bottom:.4rem; margin-bottom:1.1rem; }}

/* ── inputs ── */
.stTextInput > div > div > input {{
  background:var(--surface) !important; border:1.5px solid var(--border) !important;
  border-radius:6px !important; color:var(--text) !important;
  font-family:'Lora',serif !important; font-size:1rem !important; padding:.65rem 1rem !important;
  transition:border-color .2s, box-shadow .2s;
}}
.stTextInput > div > div > input:focus {{
  border-color:var(--accent) !important; box-shadow:0 0 0 3px var(--accent-m) !important; outline:none !important;
}}
.stTextInput label {{ display:none !important; }}

/* ── primary button ── */
.stButton > button {{
  background:var(--accent) !important; color:var(--bt) !important; border:none !important;
  border-radius:6px !important; font-family:'Bebas Neue',sans-serif !important;
  font-size:1.05rem !important; letter-spacing:.08em !important;
  padding:.6rem 1.6rem !important; width:100%; transition:all .2s !important;
}}
.stButton > button:hover {{
  background:var(--accent2) !important; box-shadow:0 6px 22px var(--accent-m) !important;
  transform:translateY(-1px);
}}

/* ── slider ── */
div[data-testid="stSlider"] label {{
  font-family:'Lora',serif !important; font-size:.8rem !important;
  color:var(--sub) !important; letter-spacing:.12em; text-transform:uppercase;
}}
.stSlider > div > div > div > div {{ background:var(--accent) !important; }}

/* ── checkbox (theme toggle) ── */
.stCheckbox label {{ font-size:.8rem !important; color:var(--sub) !important; letter-spacing:.06em; }}

/* ── movie card ── */
.m-wrap       {{ position:relative; }}
.m-card       {{
  background:var(--card); border:1px solid var(--border); border-radius:10px;
  overflow:hidden; transition:transform .25s, border-color .25s, box-shadow .25s; cursor:default;
}}
.m-card:hover {{
  transform:translateY(-7px); border-color:var(--accent);
  box-shadow:0 18px 50px rgba(0,0,0,.45);
}}
.m-card img   {{ width:100%; aspect-ratio:2/3; object-fit:cover; display:block; }}
.m-card:hover .m-hover {{ opacity:1; }}
.m-hover      {{
  position:absolute; inset:0; background:linear-gradient(to top,rgba(0,0,0,.88) 45%,transparent);
  opacity:0; transition:opacity .25s; display:flex; align-items:flex-end; padding:.8rem;
  pointer-events:none;
}}
.m-hover-txt  {{ font-family:'Lora',serif; font-size:.73rem; color:#f0ece0; line-height:1.45; }}
.m-body       {{ padding:.6rem .75rem .8rem; }}
.m-title      {{
  font-family:'Bebas Neue',sans-serif; font-size:.95rem; color:var(--text);
  white-space:nowrap; overflow:hidden; text-overflow:ellipsis; letter-spacing:.04em;
}}
.m-meta       {{ display:flex; align-items:center; gap:.3rem; flex-wrap:wrap; margin-top:.3rem; }}
.badge        {{ background:var(--accent); color:var(--bt); padding:.1rem .45rem;
                 border-radius:4px; font-size:.72rem; font-family:'Bebas Neue',sans-serif;
                 letter-spacing:.05em; }}
.gtag         {{ background:var(--surface); border:1px solid var(--border); color:var(--sub);
                 padding:.06rem .4rem; border-radius:20px; font-size:.66rem; font-family:'Lora',serif; }}
.yr           {{ font-size:.72rem; color:var(--sub); font-family:'Lora',serif; }}
.rank-num     {{
  font-family:'Bebas Neue',sans-serif; font-size:2rem; color:var(--accent);
  opacity:.4; line-height:1; padding:.3rem .5rem 0;
}}

/* ── selected movie panel ── */
.sel-wrap     {{
  background:var(--surface); border:1px solid var(--border);
  border-left:3px solid var(--accent); border-radius:10px; padding:1.3rem;
}}
.sel-title    {{ font-family:'Bebas Neue',sans-serif; font-size:1.8rem; color:var(--text);
                 letter-spacing:.04em; margin-bottom:.35rem; }}
.sel-genres   {{ font-family:'Lora',serif; font-size:.82rem; color:var(--sub); margin:.4rem 0; }}
.sel-ov       {{ font-family:'Lora',serif; font-size:.9rem; color:var(--sub);
                 line-height:1.7; margin-top:.6rem; }}

/* ── placeholder poster ── */
.ph-poster    {{
  aspect-ratio:2/3; background:var(--surface); border:2px dashed var(--border);
  border-radius:10px; display:flex; flex-direction:column; align-items:center;
  justify-content:center; text-align:center; padding:1rem;
}}
.ph-poster span {{ font-family:'Lora',serif; font-size:.85rem; color:var(--sub); line-height:1.6; }}
.ph-icon      {{ font-size:2.5rem; margin-bottom:.5rem; opacity:.4; }}

/* ── not-found banner ── */
.nf-box       {{
  background:rgba(200,60,60,.08); border:1px solid rgba(200,60,60,.22);
  border-radius:6px; padding:.75rem 1rem; margin-top:.5rem;
}}
.nf-box p     {{ font-family:'Lora',serif; font-size:.95rem; color:#e05555; margin:0; }}

/* ── suggestion pills ── */
.pill-row     {{ display:flex; flex-wrap:wrap; gap:.4rem; margin-top:.6rem; }}
.pill         {{
  background:var(--surface); border:1px solid var(--accent);
  color:var(--accent); padding:.2rem .7rem; border-radius:20px;
  font-family:'Lora',serif; font-size:.78rem; cursor:pointer;
}}

/* ── divider ── */
.divider      {{
  height:1px; background:linear-gradient(90deg,var(--accent) 0%,transparent 70%);
  margin:2rem 0; opacity:.35;
}}

/* ── no-recs warning ── */
.no-recs      {{
  background:var(--surface); border:1px solid var(--border); border-radius:6px;
  padding:1rem 1.5rem; font-family:'Lora',serif; font-size:.95rem; color:var(--sub);
}}
</style>
"""


# ─────────────────────────────────────────────────────────────────────────────
# POSTER  (local folder OR colourful placeholder — no API)
# ─────────────────────────────────────────────────────────────────────────────
POSTER_COLORS = [
    "1a1a2e/e8c547", "0d0d0d/c9a227", "1c1c1c/f0ece0",
    "0c1b33/e8c547", "2d0a0a/e8c547",
]


def poster_url(movie_id, title: str, idx: int = 0) -> str:
    """Return local path if it exists, otherwise a styled placeholder."""
    import os
    for ext in ("jpg", "png", "jpeg", "webp"):
        for folder in ("posters", "images"):
            path = f"{folder}/{movie_id}.{ext}"
            if os.path.exists(path):
                return path
    col = POSTER_COLORS[idx % len(POSTER_COLORS)]
    label = title[:14].replace(" ", "+")
    return f"https://placehold.co/300x450/{col}?text={label}"


# ─────────────────────────────────────────────────────────────────────────────
# CARD HTML
# ─────────────────────────────────────────────────────────────────────────────
def movie_card(movie: dict, card_idx: int = 0, rank: int | None = None) -> str:
    title  = movie.get("title", "Unknown")
    rating = float(movie.get("vote_average", 0))
    genres = movie.get("genres", "")
    # parse first 2 genre names from raw string
    genre_list = []
    for part in str(genres).split(",")[:2]:
        clean = part.strip().strip("[]'\"{}").split("'name':")[-1].strip().strip("'\"}")
        if clean and clean.lower() not in ("no genre",):
            genre_list.append(clean[:14])
    year   = str(movie.get("release_date", ""))[:4]
    ov     = movie.get("overview", movie.get("content",""))
    if isinstance(ov, str) and len(ov) > 130:
        ov = ov[:130] + "…"
    src    = poster_url(movie.get("id",""), title, card_idx)

    rank_html = f'<div class="rank-num">#{rank:02d}</div>' if rank else ""
    gtag_html = "".join(f'<span class="gtag">{g}</span>' for g in genre_list if g)
    yr_html   = f'<span class="yr">{year}</span>' if year.isdigit() else ""
    hover_txt = ov if ov and ov.strip() and ov.strip() not in ("nan", "NO information") else ""
    hover_html= f'<div class="m-hover"><div class="m-hover-txt">{hover_txt}</div></div>' if hover_txt else ""

    return f"""
<div class="m-wrap">
  <div class="m-card">
    {rank_html}
    <img src="{src}" alt="{title}"
         onerror="this.src='https://placehold.co/300x450/1c1c1c/e8c547?text=No+Image'"/>
    {hover_html}
    <div class="m-body">
      <div class="m-title" title="{title}">{title}</div>
      <div class="m-meta">
        <span class="badge">★ {rating:.1f}</span>
        {yr_html}
      </div>
      <div class="m-meta" style="margin-top:.25rem;">{gtag_html}</div>
    </div>
  </div>
</div>
"""


# ─────────────────────────────────────────────────────────────────────────────
# DATA PIPELINE  (cached — runs once per session)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load(_path: str = "movies.csv"):
    return build_pipeline(_path)


# ─────────────────────────────────────────────────────────────────────────────
# MAIN APP
# ─────────────────────────────────────────────────────────────────────────────
def main():
    # ── session state ─────────────────────────────────────────────────────────
    if "dark"       not in st.session_state: st.session_state.dark       = True
    if "query"      not in st.session_state: st.session_state.query      = ""
    if "searched"   not in st.session_state: st.session_state.searched   = False
    if "sel_title"  not in st.session_state: st.session_state.sel_title  = None

    # ── theme injection ───────────────────────────────────────────────────────
    theme = DARK if st.session_state.dark else LIGHT
    st.markdown(css(theme), unsafe_allow_html=True)

    # ── header row ────────────────────────────────────────────────────────────
    h1, h2 = st.columns([7, 1])
    with h1:
        st.markdown("""
        <div class="hero">
          <div class="hero-logo">Cine<em>Match</em></div>
          <div class="hero-tagline">Content-based film discovery</div>
        </div>""", unsafe_allow_html=True)
    with h2:
        st.write(""); st.write("")
        light_on = st.checkbox("☀ Light mode", value=not st.session_state.dark)
        if light_on == st.session_state.dark:
            st.session_state.dark = not light_on
            st.rerun()

    # ── load data ─────────────────────────────────────────────────────────────
    with st.spinner("Loading cinematic database…"):
        df, sim = load("movies.csv")

    # ═════════════════════════════════════════════════════════════════════════
    # SEARCH  +  POSTER  (two-column row)
    # ═════════════════════════════════════════════════════════════════════════
    search_col, poster_col = st.columns([3, 1], gap="large")

    with search_col:
        st.markdown('<div class="sec-eyebrow">Search</div>', unsafe_allow_html=True)
        input_col, btn_col = st.columns([5, 1])
        with input_col:
            query = st.text_input(
                "search", value=st.session_state.query,
                placeholder="Type a movie title…",
                label_visibility="collapsed",
            )
        with btn_col:
            st.write("")
            go = st.button("Find", use_container_width=True)

        # ── Rating slider ────────────────────────────────────────────────
        min_rating = st.slider(
            "Minimum Rating Filter", 0.0, 10.0, 5.0, 0.5,
            format="%.1f ★", help="Only show recommendations at or above this rating"
        )
        st.caption(f"Showing movies rated **{min_rating:.1f}★** and above")

    # ── trigger search ────────────────────────────────────────────────────────
    if go and query.strip():
        st.session_state.query    = query.strip()
        st.session_state.searched = True

    active_query = st.session_state.query if st.session_state.searched else ""

    # ── run recommender ───────────────────────────────────────────────────────
    sel_movie_row = None
    recs          = []
    found         = False

    if active_query:
        result = recommendor(active_query, df, sim, top_n=10, min_rating=min_rating)

        if result == "not_found":
            with search_col:
                suggestions = search_suggestions(active_query, df, n=6)
                st.markdown(
                    f'<div class="nf-box"><p>🎬 &ldquo;{active_query}&rdquo; not found in dataset.</p></div>',
                    unsafe_allow_html=True)
                if suggestions:
                    pills = "".join(f'<span class="pill">{s}</span>' for s in suggestions)
                    st.markdown(
                        f'<div style="margin-top:.5rem;font-family:Lora,serif;'
                        f'font-size:.78rem;color:var(--sub);">Did you mean:</div>'
                        f'<div class="pill-row">{pills}</div>',
                        unsafe_allow_html=True)
        else:
            found = True
            recs  = result
            # fetch the selected movie row
            rows  = df[df["title"] == active_query.lower()]
            if not rows.empty:
                sel_movie_row = rows.iloc[0].to_dict()
                st.session_state.sel_title = active_query

            # ── Selected movie info panel ─────────────────────────────────
            if sel_movie_row:
                rat  = float(sel_movie_row.get("vote_average", 0))
                raw_genres = str(sel_movie_row.get("genres", ""))
                with search_col:
                    st.markdown(f"""
                    <div class="sel-wrap" style="margin-top:.9rem;">
                      <div class="sel-title">{active_query.title()}</div>
                      <div class="m-meta">
                        <span class="badge">★ {rat:.1f}</span>
                        <span class="yr">{str(sel_movie_row.get("release_date",""))[:4]}</span>
                      </div>
                      <div class="sel-genres">{raw_genres[:120]}</div>
                    </div>""", unsafe_allow_html=True)

    # ── Selected movie poster ─────────────────────────────────────────────────
    with poster_col:
        st.markdown('<div class="sec-eyebrow">Selected Film</div>', unsafe_allow_html=True)
        if sel_movie_row:
            src = poster_url(sel_movie_row.get("id",""), active_query.title())
            st.markdown(f"""
            <div class="m-card" style="max-width:190px;margin:0 auto;">
              <img src="{src}" alt="{active_query.title()}"
                   onerror="this.src='https://placehold.co/300x450/1c1c1c/e8c547?text=No+Image'"/>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ph-poster" style="max-width:190px;margin:0 auto;">
              <div class="ph-icon">🎬</div>
              <span>Search a movie<br>to see its poster</span>
            </div>""", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # RECOMMENDATIONS  CAROUSEL
    # ═════════════════════════════════════════════════════════════════════════
    if active_query and found:
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown('<div class="sec-eyebrow">Because you watched</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="sec-head">Recommended for You</div>', unsafe_allow_html=True)

        if not recs:
            st.markdown(
                f'<div class="no-recs">No movies found with a rating ≥ {min_rating:.1f}★. '
                f'Try lowering the minimum rating slider.</div>',
                unsafe_allow_html=True)
        else:
            # Two rows of up to 5 cards each
            for row_start in (0, 5):
                batch = recs[row_start : row_start + 5]
                if not batch:
                    break
                cols = st.columns(len(batch), gap="small")
                for col, mv, ci in zip(cols, batch, range(row_start, row_start + len(batch))):
                    col.markdown(movie_card(mv, card_idx=ci), unsafe_allow_html=True)
                st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ═════════════════════════════════════════════════════════════════════════
    # TOP TRENDING SECTION
    # ═════════════════════════════════════════════════════════════════════════
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-eyebrow">Now Showing</div>', unsafe_allow_html=True)
    st.markdown('<div class="sec-head">Top Trending Films</div>', unsafe_allow_html=True)

    trending = get_trending(df, n=10)

    for row_start in (0, 5):
        batch = trending[row_start : row_start + 5]
        if not batch:
            break
        cols = st.columns(5, gap="small")
        for i, (col, mv) in enumerate(zip(cols, batch)):
            col.markdown(movie_card(mv, card_idx=row_start + i, rank=row_start + i + 1),
                         unsafe_allow_html=True)
        st.markdown("<div style='margin-bottom:1rem;'></div>", unsafe_allow_html=True)

    # ── Footer ────────────────────────────────────────────────────────────────
    st.markdown("""
    <div class="divider"></div>
    <div style="text-align:center;padding:.8rem 0;">
      <span style="font-family:'Lora',serif;font-size:.72rem;color:var(--sub);letter-spacing:.2em;">
        CINEMATCH · CONTENT-BASED RECOMMENDATION ENGINE · TF-IDF + COSINE SIMILARITY
      </span>
    </div>""", unsafe_allow_html=True)


if __name__ == "__main__":
    main()