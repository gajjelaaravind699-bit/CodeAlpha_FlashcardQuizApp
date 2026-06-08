"""
╔══════════════════════════════════════════════════════════════════╗
║              Flashcard Quiz App                                  ║
║              Built with Python 3 & Streamlit                     ║
║              Internship / Portfolio Project                      ║
║              Version : 1.0.0                                     ║
╚══════════════════════════════════════════════════════════════════╝

A professional Flashcard Quiz Application featuring:
- Flashcard CRUD management with JSON persistence
- Study Mode with card flip simulation
- Quiz Mode with scoring and performance summary
- Progress tracking and analytics with Plotly charts
- Favorites system
- Search and multi-dimensional filters
- Dark / Light theme toggle
- Responsive, internship-grade UI
"""

# ─── Standard Library ──────────────────────────────────────────────────────────
import json
import uuid
import random
from datetime import datetime
from pathlib import Path

# ─── Third-Party ───────────────────────────────────────────────────────────────
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# ═══════════════════════════════════════════════════════════════════════════════
# 1.  PAGE CONFIG  (must be first Streamlit call)
# ═══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="FlashCard Quiz App",
    page_icon="🃏",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════════════════
# 2.  CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════
FLASHCARDS_FILE = Path(__file__).parent / "flashcards.json"

CATEGORIES = [
    "Programming",
    "Mathematics",
    "Science",
    "General Knowledge",
    "History",
    "Custom",
]

DIFFICULTIES = ["Easy", "Medium", "Hard"]

DIFF_COLOR = {
    "Easy": "#22c55e",
    "Medium": "#f59e0b",
    "Hard": "#ef4444",
}

CATEGORY_ICON = {
    "Programming":       "💻",
    "Mathematics":       "📐",
    "Science":           "🔬",
    "General Knowledge": "🌍",
    "History":           "📜",
    "Custom":            "✏️",
}

PAGES = [
    ("🏠", "Dashboard"),
    ("📖", "Study Mode"),
    ("🎯", "Quiz Mode"),
    ("🗂", "Manage Cards"),
    ("⭐", "Favorites"),
    ("📊", "Statistics"),
]

# ═══════════════════════════════════════════════════════════════════════════════
# 3.  DATA LAYER  — load / save / CRUD
# ═══════════════════════════════════════════════════════════════════════════════

def load_flashcards() -> list[dict]:
    """Load flashcards from the persistent JSON file."""
    try:
        if FLASHCARDS_FILE.exists():
            with open(FLASHCARDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError) as exc:
        st.error(f"Error loading flashcards.json: {exc}")
    return []


def save_flashcards(cards: list[dict]) -> None:
    """Persist the current flashcard list to the JSON file."""
    try:
        with open(FLASHCARDS_FILE, "w", encoding="utf-8") as f:
            json.dump(cards, f, indent=2, ensure_ascii=False)
    except IOError as exc:
        st.error(f"Error saving flashcards: {exc}")


def new_card(question: str, answer: str, category: str, difficulty: str) -> dict:
    """
    Create and return a new flashcard dictionary.

    Args:
        question:   The question text.
        answer:     The answer text.
        category:   One of the defined categories.
        difficulty: Easy / Medium / Hard.

    Returns:
        A fully populated flashcard dict.
    """
    return {
        "id":         str(uuid.uuid4())[:8],
        "question":   question.strip(),
        "answer":     answer.strip(),
        "category":   category,
        "difficulty": difficulty,
        "favorite":   False,
        "studied":    False,
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }


def add_card(cards: list[dict], card: dict) -> list[dict]:
    """Append a new card to the list and save."""
    cards.append(card)
    save_flashcards(cards)
    return cards


def update_card(cards: list[dict], card_id: str, updates: dict) -> list[dict]:
    """Apply updates to the card matching card_id and save."""
    for i, c in enumerate(cards):
        if c["id"] == card_id:
            cards[i] = {**c, **updates}
            break
    save_flashcards(cards)
    return cards


def delete_card(cards: list[dict], card_id: str) -> list[dict]:
    """Remove card by ID and save."""
    cards = [c for c in cards if c["id"] != card_id]
    save_flashcards(cards)
    return cards


def toggle_favorite(cards: list[dict], card_id: str) -> list[dict]:
    """Toggle the favorite flag of a card and save."""
    for i, c in enumerate(cards):
        if c["id"] == card_id:
            cards[i]["favorite"] = not cards[i]["favorite"]
            break
    save_flashcards(cards)
    return cards


def mark_studied(cards: list[dict], card_id: str) -> list[dict]:
    """Mark a card as studied and save."""
    for i, c in enumerate(cards):
        if c["id"] == card_id:
            cards[i]["studied"] = True
            break
    save_flashcards(cards)
    return cards


def filter_cards(
    cards: list[dict],
    category: str = "All",
    difficulty: str = "All",
    search: str = "",
) -> list[dict]:
    """
    Filter cards by category, difficulty, and search term.

    Args:
        cards:      Full list of flashcard dicts.
        category:   Category name or "All".
        difficulty: Difficulty level or "All".
        search:     Free-text search (question or answer).

    Returns:
        Filtered list.
    """
    result = cards

    if category != "All":
        result = [c for c in result if c["category"] == category]

    if difficulty != "All":
        result = [c for c in result if c["difficulty"] == difficulty]

    if search.strip():
        term = search.strip().lower()
        result = [
            c for c in result
            if term in c["question"].lower()
            or term in c["answer"].lower()
            or term in c["category"].lower()
        ]

    return result


# ═══════════════════════════════════════════════════════════════════════════════
# 4.  SESSION STATE INITIALISATION
# ═══════════════════════════════════════════════════════════════════════════════

def init_state() -> None:
    """Initialise all session-state keys exactly once."""
    defaults = {
        "page":           "Dashboard",
        "dark_mode":      True,
        "cards":          load_flashcards(),
        # Study Mode
        "study_index":    0,
        "study_flipped":  False,
        "study_pool":     [],
        "study_cat":      "All",
        "study_diff":     "All",
        # Quiz Mode
        "quiz_active":    False,
        "quiz_questions": [],
        "quiz_index":     0,
        "quiz_score":     0,
        "quiz_answers":   [],   # list of dicts: {card, chosen, correct}
        "quiz_done":      False,
        "quiz_cat":       "All",
        "quiz_diff":      "All",
        "quiz_size":      10,
        # Statistics
        "quiz_history":   [],   # list of {date, score, total, pct}
        # UI helpers
        "edit_id":        None,
        "confirm_delete": None,
        "toast_msg":      "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


# ═══════════════════════════════════════════════════════════════════════════════
# 5.  THEMING — CSS injection
# ═══════════════════════════════════════════════════════════════════════════════

def inject_css(dark: bool) -> None:
    """
    Inject full custom CSS for the chosen theme.

    Args:
        dark: True = dark theme, False = light theme.
    """
    if dark:
        bg         = "#0b0f1a"
        surface    = "#131929"
        surface2   = "#1c2540"
        border     = "#263052"
        text       = "#e8eeff"
        text2      = "#8892b0"
        accent     = "#64ffda"
        accent2    = "#7b5ea7"
        btn_bg     = "#1d3461"
        btn_hover  = "#264080"
        danger     = "#ff5370"
        success    = "#64ffda"
        warn       = "#ffcb6b"
        card_sh    = "0 8px 40px rgba(100,255,218,0.08)"
        flip_bg    = "#162038"
    else:
        bg         = "#f0f4ff"
        surface    = "#ffffff"
        surface2   = "#e8eeff"
        border     = "#c5cce8"
        text       = "#1a1e35"
        text2      = "#5a6282"
        accent     = "#4361ee"
        accent2    = "#7b2d8b"
        btn_bg     = "#4361ee"
        btn_hover  = "#3451d1"
        danger     = "#e63946"
        success    = "#2ec4b6"
        warn       = "#f4a261"
        card_sh    = "0 8px 40px rgba(67,97,238,0.13)"
        flip_bg    = "#dce4ff"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Mulish:wght@300;400;500;600&display=swap');

    /* ── Reset ── */
    html, body, [class*="css"] {{
        font-family: 'Mulish', sans-serif;
        background-color: {bg} !important;
        color: {text} !important;
    }}
    #MainMenu, footer, header {{ visibility: hidden; }}
    .stDeployButton, [data-testid="stToolbar"] {{ display: none; }}

    /* ── Sidebar ── */
    [data-testid="stSidebar"] {{
        background: {surface} !important;
        border-right: 1px solid {border};
    }}
    [data-testid="stSidebar"] * {{ color: {text} !important; }}

    /* ── Block container ── */
    .main .block-container {{
        padding: 1.8rem 2.2rem 4rem;
        max-width: 1100px;
    }}

    /* ── Typography ── */
    .page-title {{
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: {accent};
        letter-spacing: -0.5px;
        margin-bottom: 0.2rem;
    }}
    .page-sub {{
        color: {text2};
        font-size: 0.9rem;
        margin-bottom: 1.8rem;
        letter-spacing: 0.03em;
    }}
    .section-head {{
        font-family: 'Syne', sans-serif;
        font-size: 1.1rem;
        font-weight: 700;
        color: {text};
        margin: 1.5rem 0 0.8rem;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        background: {btn_bg} !important;
        color: #fff !important;
        border: none !important;
        border-radius: 10px !important;
        font-family: 'Mulish', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        padding: 0.52rem 1.4rem !important;
        transition: background 0.2s, transform 0.15s !important;
        letter-spacing: 0.02em;
    }}
    .stButton > button:hover {{
        background: {btn_hover} !important;
        transform: translateY(-2px) !important;
    }}
    .stButton > button:active {{ transform: translateY(0) !important; }}

    /* Danger button */
    .danger-btn > button {{
        background: {danger} !important;
    }}
    .danger-btn > button:hover {{
        background: #c0392b !important;
    }}

    /* Success button */
    .success-btn > button {{
        background: {success} !important;
        color: #0b0f1a !important;
    }}

    /* Ghost button */
    .ghost-btn > button {{
        background: transparent !important;
        border: 1px solid {border} !important;
        color: {text} !important;
    }}
    .ghost-btn > button:hover {{
        background: {surface2} !important;
    }}

    /* ── Stat card ── */
    .stat-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        text-align: center;
        box-shadow: {card_sh};
        transition: transform 0.2s;
    }}
    .stat-card:hover {{ transform: translateY(-4px); }}
    .stat-num {{
        font-family: 'Syne', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        color: {accent};
        line-height: 1;
    }}
    .stat-lbl {{
        font-size: 0.78rem;
        color: {text2};
        margin-top: 0.35rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }}

    /* ── Flash card ── */
    .flashcard {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 22px;
        padding: 3rem 3.2rem;
        box-shadow: {card_sh};
        min-height: 260px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
        position: relative;
        overflow: hidden;
        animation: cardIn 0.4s ease;
        cursor: default;
    }}
    @keyframes cardIn {{
        from {{ opacity: 0; transform: scale(0.96) translateY(14px); }}
        to   {{ opacity: 1; transform: scale(1) translateY(0); }}
    }}
    .flashcard::before {{
        content: '';
        position: absolute;
        top: 0; left: 0;
        width: 6px; height: 100%;
        background: linear-gradient(180deg, {accent}, {accent2});
        border-radius: 22px 0 0 22px;
    }}
    .card-label {{
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: {text2};
        margin-bottom: 1.2rem;
    }}
    .card-text {{
        font-family: 'Syne', sans-serif;
        font-size: 1.32rem;
        font-weight: 600;
        line-height: 1.65;
        color: {text};
        flex: 1;
    }}
    .card-answer {{
        font-size: 1.05rem;
        font-weight: 400;
        line-height: 1.75;
        color: {text};
        flex: 1;
        font-family: 'Mulish', sans-serif;
    }}
    .card-meta {{
        margin-top: 1.5rem;
        display: flex;
        gap: 0.6rem;
        align-items: center;
    }}

    /* Flipped card highlight */
    .flashcard-answer {{
        background: {flip_bg};
    }}

    /* ── Diff / category badges ── */
    .badge {{
        display: inline-block;
        font-size: 0.72rem;
        font-weight: 700;
        padding: 0.2rem 0.7rem;
        border-radius: 99px;
        letter-spacing: 0.05em;
    }}
    .badge-easy   {{ background: #16a34a22; color: #22c55e; }}
    .badge-medium {{ background: #d9770622; color: #f59e0b; }}
    .badge-hard   {{ background: #dc262622; color: #ef4444; }}
    .badge-cat    {{ background: {surface2}; color: {text2}; }}

    /* ── Quiz option buttons ── */
    .quiz-opt > button {{
        background: {surface2} !important;
        color: {text} !important;
        border: 1px solid {border} !important;
        border-radius: 12px !important;
        text-align: left !important;
        padding: 0.85rem 1.2rem !important;
        font-size: 0.92rem !important;
        width: 100% !important;
        margin-bottom: 0.5rem;
        transition: all 0.18s !important;
    }}
    .quiz-opt > button:hover {{
        border-color: {accent} !important;
        color: {accent} !important;
        background: {surface} !important;
    }}
    .quiz-correct > button {{
        background: #16a34a22 !important;
        border-color: #22c55e !important;
        color: #22c55e !important;
    }}
    .quiz-wrong > button {{
        background: #dc262622 !important;
        border-color: #ef4444 !important;
        color: #ef4444 !important;
    }}

    /* ── List card (manage) ── */
    .list-card {{
        background: {surface};
        border: 1px solid {border};
        border-radius: 14px;
        padding: 1.1rem 1.4rem;
        margin-bottom: 0.8rem;
        transition: transform 0.2s, box-shadow 0.2s;
        animation: cardIn 0.3s ease;
    }}
    .list-card:hover {{
        transform: translateX(4px);
        box-shadow: {card_sh};
    }}
    .list-q {{
        font-family: 'Syne', sans-serif;
        font-weight: 600;
        font-size: 0.98rem;
        color: {text};
        margin-bottom: 0.3rem;
    }}
    .list-a {{
        font-size: 0.83rem;
        color: {text2};
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        max-width: 600px;
    }}

    /* ── Sidebar nav ── */
    .nav-item > button {{
        width: 100% !important;
        text-align: left !important;
        background: transparent !important;
        color: {text} !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 0.9rem !important;
        font-size: 0.9rem !important;
        font-weight: 500 !important;
        margin-bottom: 0.2rem;
        transition: all 0.18s !important;
    }}
    .nav-item > button:hover {{
        background: {surface2} !important;
        color: {accent} !important;
    }}
    .nav-active > button {{
        background: {surface2} !important;
        color: {accent} !important;
        font-weight: 700 !important;
        border-left: 3px solid {accent} !important;
    }}

    /* ── Progress bar ── */
    .prog-wrap {{
        height: 8px;
        background: {surface2};
        border-radius: 99px;
        overflow: hidden;
        margin: 0.6rem 0 1rem;
    }}
    .prog-fill {{
        height: 100%;
        background: linear-gradient(90deg, {accent}, {accent2});
        border-radius: 99px;
        transition: width 0.4s ease;
    }}

    /* ── Score ring (SVG) ── */
    .score-ring-wrap {{
        display: flex;
        justify-content: center;
        margin: 1.5rem 0;
    }}

    /* ── Divider ── */
    .divider {{
        border: none;
        border-top: 1px solid {border};
        margin: 1.5rem 0;
    }}

    /* ── Inputs / Select ── */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {{
        background: {surface} !important;
        border-color: {border} !important;
        color: {text} !important;
        border-radius: 10px !important;
    }}

    /* ── Footer ── */
    .footer {{
        margin-top: 4rem;
        padding-top: 1.2rem;
        border-top: 1px solid {border};
        text-align: center;
        color: {text2};
        font-size: 0.8rem;
        line-height: 2;
    }}
    .footer a {{ color: {accent}; text-decoration: none; }}

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {{ width: 5px; }}
    ::-webkit-scrollbar-track {{ background: transparent; }}
    ::-webkit-scrollbar-thumb {{ background: {border}; border-radius: 99px; }}
    </style>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════════════════
# 6.  SHARED HELPERS
# ═══════════════════════════════════════════════════════════════════════════════

def diff_badge(diff: str) -> str:
    """Return an HTML badge string for a difficulty level."""
    cls = f"badge-{diff.lower()}"
    return f"<span class='badge {cls}'>{diff}</span>"


def cat_badge(cat: str) -> str:
    """Return an HTML badge string for a category."""
    icon = CATEGORY_ICON.get(cat, "📌")
    return f"<span class='badge badge-cat'>{icon} {cat}</span>"


def progress_bar(current: int, total: int) -> str:
    """Return an HTML progress bar for current/total."""
    pct = int(current / total * 100) if total else 0
    return (
        f"<div class='prog-wrap'>"
        f"<div class='prog-fill' style='width:{pct}%'></div>"
        f"</div>"
    )


def stat_card(num: int | str, label: str) -> str:
    """Return HTML for a statistics card."""
    return (
        f"<div class='stat-card'>"
        f"<div class='stat-num'>{num}</div>"
        f"<div class='stat-lbl'>{label}</div>"
        f"</div>"
    )


def make_plotly_layout(dark: bool) -> dict:
    """Return common Plotly layout kwargs matching the current theme."""
    bg    = "#0b0f1a" if dark else "#f0f4ff"
    paper = "#131929" if dark else "#ffffff"
    text  = "#e8eeff" if dark else "#1a1e35"
    grid  = "#263052" if dark else "#c5cce8"
    return dict(
        plot_bgcolor=paper,
        paper_bgcolor=paper,
        font_color=text,
        xaxis=dict(gridcolor=grid, linecolor=grid),
        yaxis=dict(gridcolor=grid, linecolor=grid),
        margin=dict(l=20, r=20, t=40, b=20),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 7.  SIDEBAR
# ═══════════════════════════════════════════════════════════════════════════════

def render_sidebar() -> None:
    """Render the left sidebar with branding, navigation, and quick stats."""
    cards = st.session_state.cards

    with st.sidebar:
        # Brand
        st.markdown(
            "<div style='font-family:Syne,sans-serif;font-size:1.55rem;"
            "font-weight:800;margin-bottom:0.2rem;'>🃏 FlashCard App</div>"
            "<div style='font-size:0.75rem;opacity:0.45;letter-spacing:0.1em;"
            "text-transform:uppercase;margin-bottom:1.4rem;'>Internship Project</div>",
            unsafe_allow_html=True,
        )

        st.markdown("---")

        # Navigation
        st.markdown(
            "<div style='font-size:0.72rem;font-weight:700;letter-spacing:0.12em;"
            "text-transform:uppercase;opacity:0.45;margin-bottom:0.5rem;'>Menu</div>",
            unsafe_allow_html=True,
        )

        for icon, label in PAGES:
            is_active = st.session_state.page == label
            css = "nav-active" if is_active else "nav-item"
            st.markdown(f"<div class='{css}'>", unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{label}", use_container_width=True):
                # Reset study/quiz state when switching pages
                if label == "Study Mode":
                    st.session_state.study_index   = 0
                    st.session_state.study_flipped  = False
                if label == "Quiz Mode":
                    st.session_state.quiz_active    = False
                    st.session_state.quiz_done      = False
                st.session_state.page = label
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("---")

        # Theme toggle
        mode_lbl = "☀️  Light Mode" if st.session_state.dark_mode else "🌙  Dark Mode"
        if st.button(mode_lbl, use_container_width=True, key="theme_toggle"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()

        st.markdown("---")

        # Quick stats
        total    = len(cards)
        studied  = sum(1 for c in cards if c.get("studied"))
        favs     = sum(1 for c in cards if c.get("favorite"))
        cats_cnt = len({c["category"] for c in cards})
        st.markdown(
            f"<div style='font-size:0.72rem;font-weight:700;opacity:0.45;"
            f"letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.6rem;'>Quick Stats</div>"
            f"<div style='font-size:0.86rem;line-height:2.2;'>"
            f"🃏  {total} Flashcards<br>"
            f"✅  {studied} Studied<br>"
            f"⭐  {favs} Favorites<br>"
            f"🗂  {cats_cnt} Categories"
            f"</div>",
            unsafe_allow_html=True,
        )

        st.markdown("---")
        st.markdown(
            "<div style='font-size:0.7rem;opacity:0.35;text-align:center;line-height:1.8;'>"
            "Built with Python &amp; Streamlit<br>Internship Project 2024"
            "</div>",
            unsafe_allow_html=True,
        )


# ═══════════════════════════════════════════════════════════════════════════════
# 8.  PAGE — DASHBOARD
# ═══════════════════════════════════════════════════════════════════════════════

def page_dashboard() -> None:
    """Render the Dashboard overview page."""
    cards = st.session_state.cards

    st.markdown(
        "<div class='page-title'>🏠 Dashboard</div>"
        "<div class='page-sub'>Your learning hub — overview, stats, and quick actions</div>",
        unsafe_allow_html=True,
    )

    # ── Top stats ──────────────────────────────────────────────────────────────
    total    = len(cards)
    studied  = sum(1 for c in cards if c.get("studied"))
    favs     = sum(1 for c in cards if c.get("favorite"))
    attempts = len(st.session_state.quiz_history)
    avg_sc   = (
        round(sum(q["pct"] for q in st.session_state.quiz_history) / attempts)
        if attempts else 0
    )
    cats_cnt = len({c["category"] for c in cards})

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    for col, num, lbl in zip(
        [c1, c2, c3, c4, c5, c6],
        [total, studied, cats_cnt, attempts, f"{avg_sc}%", favs],
        ["Total Cards", "Studied", "Categories", "Quiz Attempts", "Avg Score", "Favorites"],
    ):
        with col:
            st.markdown(stat_card(num, lbl), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Category breakdown bar ─────────────────────────────────────────────────
    cat_counts = {}
    for c in cards:
        cat_counts[c["category"]] = cat_counts.get(c["category"], 0) + 1

    if cat_counts:
        fig = go.Figure(
            go.Bar(
                x=list(cat_counts.keys()),
                y=list(cat_counts.values()),
                marker_color=["#64ffda", "#7b5ea7", "#ff6b6b", "#ffd166", "#06d6a0", "#118ab2"],
                text=list(cat_counts.values()),
                textposition="outside",
            )
        )
        layout = make_plotly_layout(st.session_state.dark_mode)
        fig.update_layout(
            title="Flashcards by Category",
            showlegend=False,
            height=320,
            **{k: v for k, v in layout.items() if k not in ("xaxis", "yaxis")},
        )
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)

    # ── Difficulty distribution ────────────────────────────────────────────────
    diff_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
    for c in cards:
        diff_counts[c.get("difficulty", "Easy")] += 1

    col_pie, col_recent = st.columns([1, 2])

    with col_pie:
        fig2 = go.Figure(
            go.Pie(
                labels=list(diff_counts.keys()),
                values=list(diff_counts.values()),
                marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
                hole=0.55,
                textinfo="label+percent",
            )
        )
        fig2.update_layout(
            title="Difficulty Distribution",
            showlegend=False,
            height=300,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#e8eeff" if st.session_state.dark_mode else "#1a1e35",
            margin=dict(l=10, r=10, t=40, b=10),
        )
        st.plotly_chart(fig2, use_container_width=True)

    with col_recent:
        st.markdown("<div class='section-head'>Recently Added Cards</div>", unsafe_allow_html=True)
        recent = sorted(cards, key=lambda c: c.get("created_at", ""), reverse=True)[:5]
        if recent:
            for c in recent:
                st.markdown(
                    f"<div class='list-card'>"
                    f"<div class='list-q'>{c['question'][:80]}{'...' if len(c['question'])>80 else ''}</div>"
                    f"<div class='list-a'>{c['answer'][:100]}{'...' if len(c['answer'])>100 else ''}</div>"
                    f"<div class='card-meta'>{diff_badge(c['difficulty'])} {cat_badge(c['category'])}</div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        else:
            st.info("No flashcards yet. Go to **Manage Cards** to add some!")

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 9.  PAGE — STUDY MODE
# ═══════════════════════════════════════════════════════════════════════════════

def page_study() -> None:
    """Render Study Mode: one card at a time with flip and navigation."""
    st.markdown(
        "<div class='page-title'>📖 Study Mode</div>"
        "<div class='page-sub'>Review flashcards at your own pace — flip to see the answer</div>",
        unsafe_allow_html=True,
    )

    cards = st.session_state.cards

    # ── Filters ────────────────────────────────────────────────────────────────
    fc1, fc2, fc3, fc4 = st.columns([2, 1, 1, 1])
    with fc1:
        search = st.text_input("🔍 Search", placeholder="Question or keyword…", key="study_search")
    with fc2:
        cat = st.selectbox(
            "Category",
            ["All"] + CATEGORIES,
            key="study_cat_select",
        )
    with fc3:
        diff = st.selectbox("Difficulty", ["All"] + DIFFICULTIES, key="study_diff_select")
    with fc4:
        fav_only = st.checkbox("⭐ Favorites Only", key="study_fav_only")

    pool = filter_cards(cards, cat, diff, search)
    if fav_only:
        pool = [c for c in pool if c.get("favorite")]

    if not pool:
        st.warning("No flashcards match the current filters.")
        return

    # Reset index if pool changed size significantly
    if st.session_state.study_index >= len(pool):
        st.session_state.study_index = 0
        st.session_state.study_flipped = False

    idx    = st.session_state.study_index
    card   = pool[idx]
    total  = len(pool)
    flipped = st.session_state.study_flipped

    # ── Counter + progress ─────────────────────────────────────────────────────
    st.markdown(
        f"<div style='font-size:0.85rem;color:#8892b0;margin-bottom:0.3rem;'>"
        f"Card <strong>{idx+1}</strong> of <strong>{total}</strong></div>",
        unsafe_allow_html=True,
    )
    st.markdown(progress_bar(idx + 1, total), unsafe_allow_html=True)

    # ── Flashcard ──────────────────────────────────────────────────────────────
    if flipped:
        st.markdown(
            f"<div class='flashcard flashcard-answer'>"
            f"<div class='card-label'>✅ Answer</div>"
            f"<div class='card-answer'>{card['answer']}</div>"
            f"<div class='card-meta'>{diff_badge(card['difficulty'])} {cat_badge(card['category'])}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            f"<div class='flashcard'>"
            f"<div class='card-label'>❓ Question</div>"
            f"<div class='card-text'>{card['question']}</div>"
            f"<div class='card-meta'>{diff_badge(card['difficulty'])} {cat_badge(card['category'])}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    # ── Action buttons ─────────────────────────────────────────────────────────
    b1, b2, b3, b4, b5 = st.columns(5)

    with b1:
        st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
        if st.button("⬅ Previous", use_container_width=True, key="study_prev"):
            st.session_state.study_index = (idx - 1) % total
            st.session_state.study_flipped = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    with b2:
        flip_lbl = "🔄 Show Question" if flipped else "🔄 Flip Card"
        if st.button(flip_lbl, use_container_width=True, key="study_flip"):
            st.session_state.study_flipped = not flipped
            # Mark as studied when answer is revealed
            if not flipped:
                st.session_state.cards = mark_studied(st.session_state.cards, card["id"])
            st.rerun()

    with b3:
        if st.button("➡ Next", use_container_width=True, key="study_next"):
            st.session_state.study_index = (idx + 1) % total
            st.session_state.study_flipped = False
            st.rerun()

    with b4:
        if st.button("🔀 Shuffle", use_container_width=True, key="study_shuffle"):
            random.shuffle(pool)
            st.session_state.study_index = 0
            st.session_state.study_flipped = False
            st.toast("Cards shuffled!", icon="🔀")
            st.rerun()

    with b5:
        is_fav = card.get("favorite", False)
        fav_lbl = "★ Unfavorite" if is_fav else "☆ Favorite"
        st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
        if st.button(fav_lbl, use_container_width=True, key="study_fav"):
            st.session_state.cards = toggle_favorite(st.session_state.cards, card["id"])
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 10.  PAGE — QUIZ MODE
# ═══════════════════════════════════════════════════════════════════════════════

def build_quiz_questions(pool: list[dict], size: int, all_cards: list[dict]) -> list[dict]:
    """
    Build a list of quiz question dicts with 4 options (1 correct, 3 wrong).

    Args:
        pool:      Filtered set of cards to pull questions from.
        size:      Number of questions to include.
        all_cards: Full card list (used to source wrong answers).

    Returns:
        List of question dicts.
    """
    chosen = random.sample(pool, min(size, len(pool)))
    questions = []
    for card in chosen:
        # Build wrong answers from other cards in any category
        wrong_pool = [c for c in all_cards if c["id"] != card["id"]]
        wrongs = random.sample(wrong_pool, min(3, len(wrong_pool)))
        options = [card["answer"]] + [w["answer"] for w in wrongs]
        random.shuffle(options)
        questions.append({
            "card":    card,
            "options": options,
            "correct": card["answer"],
        })
    return questions


def page_quiz() -> None:
    """Render Quiz Mode: multiple-choice quiz with scoring and summary."""
    st.markdown(
        "<div class='page-title'>🎯 Quiz Mode</div>"
        "<div class='page-sub'>Test your knowledge — answer multiple-choice questions</div>",
        unsafe_allow_html=True,
    )

    cards = st.session_state.cards

    # ── Quiz Setup ─────────────────────────────────────────────────────────────
    if not st.session_state.quiz_active and not st.session_state.quiz_done:
        st.markdown("<div class='section-head'>Quiz Settings</div>", unsafe_allow_html=True)

        qc1, qc2, qc3 = st.columns(3)
        with qc1:
            q_cat = st.selectbox("Category", ["All"] + CATEGORIES, key="qset_cat")
        with qc2:
            q_diff = st.selectbox("Difficulty", ["All"] + DIFFICULTIES, key="qset_diff")
        with qc3:
            q_size = st.slider("Number of Questions", 5, 30, 10, key="qset_size")

        pool = filter_cards(cards, q_cat, q_diff, "")
        st.markdown(
            f"<div style='margin:0.5rem 0 1.2rem;font-size:0.9rem;'>"
            f"<strong>{len(pool)}</strong> cards available for this quiz.</div>",
            unsafe_allow_html=True,
        )

        if len(pool) < 4:
            st.warning("Need at least 4 cards to generate a quiz. Add more cards or broaden the filters.")
            return

        if st.button("🚀 Start Quiz", use_container_width=False):
            questions = build_quiz_questions(pool, q_size, cards)
            st.session_state.quiz_questions = questions
            st.session_state.quiz_index     = 0
            st.session_state.quiz_score     = 0
            st.session_state.quiz_answers   = []
            st.session_state.quiz_active    = True
            st.session_state.quiz_done      = False
            st.rerun()
        return

    # ── Quiz Results ───────────────────────────────────────────────────────────
    if st.session_state.quiz_done:
        questions = st.session_state.quiz_questions
        score     = st.session_state.quiz_score
        total_q   = len(questions)
        pct       = round(score / total_q * 100) if total_q else 0
        wrong     = total_q - score

        # Save to history
        if (
            not st.session_state.quiz_history
            or st.session_state.quiz_history[-1].get("pct") != pct
        ):
            st.session_state.quiz_history.append({
                "date":  datetime.now().strftime("%Y-%m-%d %H:%M"),
                "score": score,
                "total": total_q,
                "pct":   pct,
            })

        # Score ring
        ring_color = "#22c55e" if pct >= 70 else ("#f59e0b" if pct >= 40 else "#ef4444")
        grade = "Excellent! 🎉" if pct >= 90 else ("Good Job! 👍" if pct >= 70 else ("Keep Practising! 💪" if pct >= 40 else "Need More Study 📚"))

        fig_ring = go.Figure(go.Pie(
            values=[pct, 100 - pct],
            hole=0.72,
            marker_colors=[ring_color, "#263052"],
            textinfo="none",
        ))
        fig_ring.add_annotation(
            text=f"<b>{pct}%</b>",
            x=0.5, y=0.5,
            font=dict(size=36, color=ring_color, family="Syne"),
            showarrow=False,
        )
        fig_ring.update_layout(
            showlegend=False,
            height=260,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=10, r=10, t=10, b=10),
        )

        rc1, rc2 = st.columns([1, 2])
        with rc1:
            st.plotly_chart(fig_ring, use_container_width=True)
            st.markdown(
                f"<div style='text-align:center;font-family:Syne,sans-serif;"
                f"font-size:1.1rem;font-weight:700;'>{grade}</div>",
                unsafe_allow_html=True,
            )

        with rc2:
            st.markdown("<div class='section-head'>Performance Summary</div>", unsafe_allow_html=True)
            sc1, sc2, sc3 = st.columns(3)
            with sc1:
                st.markdown(stat_card(score, "Correct"), unsafe_allow_html=True)
            with sc2:
                st.markdown(stat_card(wrong, "Wrong"), unsafe_allow_html=True)
            with sc3:
                st.markdown(stat_card(total_q, "Total"), unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # Per-question review
            st.markdown("<div class='section-head'>Question Review</div>", unsafe_allow_html=True)
            for i, qa in enumerate(st.session_state.quiz_answers):
                is_correct = qa["chosen"] == qa["correct"]
                icon = "✅" if is_correct else "❌"
                st.markdown(
                    f"<div class='list-card'>"
                    f"<div class='list-q'>{icon} Q{i+1}: {qa['card']['question'][:80]}</div>"
                    f"<div class='list-a'><strong>Your answer:</strong> {qa['chosen'][:80]}</div>"
                    f"{'<div class=\"list-a\"><strong>Correct:</strong> '+qa['correct'][:80]+'</div>' if not is_correct else ''}"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Restart / Home
        rb1, rb2 = st.columns(2)
        with rb1:
            if st.button("🔄 Retake Quiz", use_container_width=True):
                st.session_state.quiz_active = False
                st.session_state.quiz_done   = False
                st.rerun()
        with rb2:
            st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
            if st.button("🏠 Go to Dashboard", use_container_width=True):
                st.session_state.quiz_active = False
                st.session_state.quiz_done   = False
                st.session_state.page        = "Dashboard"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
        return

    # ── Active Quiz ────────────────────────────────────────────────────────────
    questions = st.session_state.quiz_questions
    q_idx     = st.session_state.quiz_index
    total_q   = len(questions)

    if q_idx >= total_q:
        st.session_state.quiz_done   = True
        st.session_state.quiz_active = False
        st.rerun()
        return

    current = questions[q_idx]
    card    = current["card"]

    # Progress
    st.markdown(
        f"<div style='font-size:0.85rem;color:#8892b0;margin-bottom:0.3rem;'>"
        f"Question <strong>{q_idx+1}</strong> of <strong>{total_q}</strong> "
        f"&nbsp;|&nbsp; Score: <strong>{st.session_state.quiz_score}</strong></div>",
        unsafe_allow_html=True,
    )
    st.markdown(progress_bar(q_idx + 1, total_q), unsafe_allow_html=True)

    # Question card
    st.markdown(
        f"<div class='flashcard'>"
        f"<div class='card-label'>❓ Question {q_idx+1}</div>"
        f"<div class='card-text'>{card['question']}</div>"
        f"<div class='card-meta'>{diff_badge(card['difficulty'])} {cat_badge(card['category'])}</div>"
        f"</div>",
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("<div style='font-weight:600;font-size:0.9rem;margin-bottom:0.5rem;'>Choose the correct answer:</div>", unsafe_allow_html=True)

    # Options
    for opt in current["options"]:
        st.markdown("<div class='quiz-opt'>", unsafe_allow_html=True)
        short_opt = opt[:100] + ("…" if len(opt) > 100 else "")
        if st.button(short_opt, key=f"opt_{q_idx}_{opt[:30]}", use_container_width=True):
            is_correct = (opt == current["correct"])
            if is_correct:
                st.session_state.quiz_score += 1
                st.toast("Correct! ✅", icon="✅")
            else:
                st.toast("Wrong ❌", icon="❌")
            st.session_state.quiz_answers.append({
                "card":    card,
                "chosen":  opt,
                "correct": current["correct"],
            })
            st.session_state.quiz_index += 1
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # Skip button
    st.markdown("<div class='ghost-btn' style='margin-top:0.5rem;'>", unsafe_allow_html=True)
    if st.button("⏭ Skip Question", key=f"skip_{q_idx}"):
        st.session_state.quiz_answers.append({
            "card":    card,
            "chosen":  "(Skipped)",
            "correct": current["correct"],
        })
        st.session_state.quiz_index += 1
        st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 11.  PAGE — MANAGE CARDS
# ═══════════════════════════════════════════════════════════════════════════════

def page_manage() -> None:
    """Render the Manage Cards page: create, edit, delete, import, export."""
    st.markdown(
        "<div class='page-title'>🗂 Manage Flashcards</div>"
        "<div class='page-sub'>Create, edit, delete, import and export your flashcards</div>",
        unsafe_allow_html=True,
    )

    cards = st.session_state.cards

    tab_list, tab_add, tab_import = st.tabs(["📋 All Cards", "➕ Add New Card", "📁 Import / Export"])

    # ── Tab 1: All Cards ───────────────────────────────────────────────────────
    with tab_list:
        # Filters
        mc1, mc2, mc3 = st.columns([2, 1, 1])
        with mc1:
            m_search = st.text_input("🔍 Search cards", key="manage_search", placeholder="Question, answer, or category…")
        with mc2:
            m_cat = st.selectbox("Category", ["All"] + CATEGORIES, key="manage_cat")
        with mc3:
            m_diff = st.selectbox("Difficulty", ["All"] + DIFFICULTIES, key="manage_diff")

        visible = filter_cards(cards, m_cat, m_diff, m_search)

        st.markdown(
            f"<div style='margin:0.4rem 0 1rem;font-size:0.85rem;color:#8892b0;'>"
            f"Showing <strong>{len(visible)}</strong> of <strong>{len(cards)}</strong> cards</div>",
            unsafe_allow_html=True,
        )

        if not visible:
            st.info("No cards match the current filters.")
        else:
            for card in visible:
                # Edit mode
                if st.session_state.edit_id == card["id"]:
                    with st.expander(f"✏️ Editing: {card['question'][:60]}…", expanded=True):
                        eq  = st.text_area("Question", card["question"], key=f"eq_{card['id']}")
                        ea  = st.text_area("Answer",   card["answer"],   key=f"ea_{card['id']}")
                        ec1, ec2 = st.columns(2)
                        with ec1:
                            ecat = st.selectbox("Category",   CATEGORIES,   index=CATEGORIES.index(card["category"]),   key=f"ecat_{card['id']}")
                        with ec2:
                            edif = st.selectbox("Difficulty",  DIFFICULTIES, index=DIFFICULTIES.index(card["difficulty"]), key=f"edif_{card['id']}")

                        sb1, sb2 = st.columns(2)
                        with sb1:
                            if st.button("💾 Save", key=f"save_{card['id']}", use_container_width=True):
                                st.session_state.cards = update_card(
                                    st.session_state.cards, card["id"],
                                    {"question": eq, "answer": ea, "category": ecat, "difficulty": edif},
                                )
                                st.session_state.edit_id = None
                                st.toast("Card updated!", icon="💾")
                                st.rerun()
                        with sb2:
                            st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
                            if st.button("✖ Cancel", key=f"cancel_{card['id']}", use_container_width=True):
                                st.session_state.edit_id = None
                                st.rerun()
                            st.markdown("</div>", unsafe_allow_html=True)
                    continue

                # Normal view
                fav_icon = "★" if card.get("favorite") else "☆"
                st.markdown(
                    f"<div class='list-card'>"
                    f"<div class='list-q'>{fav_icon} {card['question'][:80]}{'…' if len(card['question'])>80 else ''}</div>"
                    f"<div class='list-a'>{card['answer'][:120]}{'…' if len(card['answer'])>120 else ''}</div>"
                    f"<div class='card-meta' style='margin-top:0.6rem;'>{diff_badge(card['difficulty'])} {cat_badge(card['category'])}"
                    f"<span style='font-size:0.72rem;opacity:0.4;margin-left:0.5rem;'>ID: {card['id']}</span></div>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

                ab1, ab2, ab3, ab4 = st.columns([1, 1, 1, 4])
                with ab1:
                    if st.button("✏️", key=f"edit_{card['id']}", help="Edit card"):
                        st.session_state.edit_id = card["id"]
                        st.rerun()
                with ab2:
                    fav_tt = "Remove from favorites" if card.get("favorite") else "Add to favorites"
                    if st.button("⭐", key=f"fav_{card['id']}", help=fav_tt):
                        st.session_state.cards = toggle_favorite(st.session_state.cards, card["id"])
                        st.rerun()
                with ab3:
                    st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{card['id']}", help="Delete card"):
                        st.session_state.confirm_delete = card["id"]
                        st.rerun()
                    st.markdown("</div>", unsafe_allow_html=True)

                # Confirm delete
                if st.session_state.confirm_delete == card["id"]:
                    st.warning(f"Delete **{card['question'][:60]}**? This cannot be undone.")
                    conf1, conf2 = st.columns(2)
                    with conf1:
                        st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
                        if st.button("Yes, Delete", key=f"confirm_{card['id']}", use_container_width=True):
                            st.session_state.cards = delete_card(st.session_state.cards, card["id"])
                            st.session_state.confirm_delete = None
                            st.toast("Card deleted.", icon="🗑️")
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)
                    with conf2:
                        st.markdown("<div class='ghost-btn'>", unsafe_allow_html=True)
                        if st.button("Cancel", key=f"noconfirm_{card['id']}", use_container_width=True):
                            st.session_state.confirm_delete = None
                            st.rerun()
                        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 2: Add New Card ────────────────────────────────────────────────────
    with tab_add:
        st.markdown("<div class='section-head'>Create a New Flashcard</div>", unsafe_allow_html=True)

        n_q  = st.text_area("Question *", placeholder="Enter your question here…", key="new_q", height=100)
        n_a  = st.text_area("Answer *",   placeholder="Enter the answer here…",   key="new_a", height=120)

        nc1, nc2 = st.columns(2)
        with nc1:
            n_cat  = st.selectbox("Category",   CATEGORIES,   key="new_cat")
        with nc2:
            n_diff = st.selectbox("Difficulty", DIFFICULTIES, key="new_diff")

        if st.button("➕ Add Flashcard", use_container_width=False):
            if not n_q.strip() or not n_a.strip():
                st.error("Both Question and Answer are required.")
            else:
                card = new_card(n_q, n_a, n_cat, n_diff)
                st.session_state.cards = add_card(st.session_state.cards, card)
                st.toast("Flashcard added! ✅", icon="✅")
                st.rerun()

    # ── Tab 3: Import / Export ─────────────────────────────────────────────────
    with tab_import:
        ie1, ie2 = st.columns(2)

        with ie1:
            st.markdown("<div class='section-head'>📤 Export Flashcards</div>", unsafe_allow_html=True)
            st.write(f"Export all **{len(cards)}** flashcards as a JSON file.")
            json_str = json.dumps(cards, indent=2, ensure_ascii=False)
            st.download_button(
                label="⬇️ Download flashcards.json",
                data=json_str,
                file_name="flashcards_export.json",
                mime="application/json",
                use_container_width=True,
            )

        with ie2:
            st.markdown("<div class='section-head'>📥 Import Flashcards</div>", unsafe_allow_html=True)
            st.write("Upload a JSON file containing flashcards. Duplicate IDs will be skipped.")
            uploaded = st.file_uploader("Choose JSON file", type=["json"], key="import_upload")
            if uploaded:
                try:
                    imported = json.load(uploaded)
                    if not isinstance(imported, list):
                        st.error("File must contain a JSON array of flashcard objects.")
                    else:
                        existing_ids = {c["id"] for c in st.session_state.cards}
                        new_cards    = [c for c in imported if c.get("id") not in existing_ids]
                        st.session_state.cards.extend(new_cards)
                        save_flashcards(st.session_state.cards)
                        st.success(f"Imported {len(new_cards)} new cards. {len(imported)-len(new_cards)} duplicates skipped.")
                        st.rerun()
                except (json.JSONDecodeError, ValueError) as e:
                    st.error(f"Invalid JSON file: {e}")

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 12.  PAGE — FAVORITES
# ═══════════════════════════════════════════════════════════════════════════════

def page_favorites() -> None:
    """Render the Favorites page: view and manage favorite flashcards."""
    st.markdown(
        "<div class='page-title'>⭐ Favorites</div>"
        "<div class='page-sub'>Your hand-picked collection of important flashcards</div>",
        unsafe_allow_html=True,
    )

    cards = st.session_state.cards
    favs  = [c for c in cards if c.get("favorite")]

    if not favs:
        st.info(
            "You haven't favorited any cards yet. "
            "In **Study Mode** or **Manage Cards**, click ⭐ to save a card here."
        )
        render_footer()
        return

    st.markdown(
        f"<div style='margin-bottom:1.2rem;'>"
        f"<span style='background:#2563eb22;color:#64ffda;padding:0.25rem 0.8rem;"
        f"border-radius:99px;font-size:0.82rem;font-weight:700;'>⭐ {len(favs)} Favorites</span>"
        f"</div>",
        unsafe_allow_html=True,
    )

    # Filter favorites
    fs1, fs2 = st.columns([2, 1])
    with fs1:
        fsearch = st.text_input("🔍 Search favorites", key="fav_search", placeholder="Question or answer…")
    with fs2:
        fcat = st.selectbox("Category", ["All"] + CATEGORIES, key="fav_cat")

    visible_favs = filter_cards(favs, fcat, "All", fsearch)

    for card in visible_favs:
        st.markdown(
            f"<div class='list-card'>"
            f"<div class='list-q'>★ {card['question'][:80]}{'…' if len(card['question'])>80 else ''}</div>"
            f"<div class='list-a'>{card['answer'][:150]}{'…' if len(card['answer'])>150 else ''}</div>"
            f"<div class='card-meta' style='margin-top:0.6rem;'>{diff_badge(card['difficulty'])} {cat_badge(card['category'])}</div>"
            f"</div>",
            unsafe_allow_html=True,
        )

        rb1, rb2 = st.columns([1, 6])
        with rb1:
            st.markdown("<div class='danger-btn'>", unsafe_allow_html=True)
            if st.button("★ Remove", key=f"unfav_{card['id']}", use_container_width=True):
                st.session_state.cards = toggle_favorite(st.session_state.cards, card["id"])
                st.toast("Removed from Favorites.", icon="🗑️")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 13.  PAGE — STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

def page_statistics() -> None:
    """Render the Statistics page with charts and learning analytics."""
    st.markdown(
        "<div class='page-title'>📊 Statistics</div>"
        "<div class='page-sub'>Learning analytics and performance insights</div>",
        unsafe_allow_html=True,
    )

    cards   = st.session_state.cards
    history = st.session_state.quiz_history

    # ── Top stats ──────────────────────────────────────────────────────────────
    total    = len(cards)
    studied  = sum(1 for c in cards if c.get("studied"))
    favs     = sum(1 for c in cards if c.get("favorite"))
    attempts = len(history)
    avg_pct  = round(sum(h["pct"] for h in history) / attempts) if attempts else 0
    accuracy = round(studied / total * 100) if total else 0

    sc1, sc2, sc3, sc4, sc5, sc6 = st.columns(6)
    for col, num, lbl in zip(
        [sc1, sc2, sc3, sc4, sc5, sc6],
        [total, studied, f"{accuracy}%", attempts, f"{avg_pct}%", favs],
        ["Total Cards", "Studied", "Study Rate", "Quiz Attempts", "Avg Score", "Favorites"],
    ):
        with col:
            st.markdown(stat_card(num, lbl), unsafe_allow_html=True)

    st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

    # ── Category chart ─────────────────────────────────────────────────────────
    cat_counts = {}
    cat_studied = {}
    for c in cards:
        cat = c["category"]
        cat_counts[cat]  = cat_counts.get(cat, 0) + 1
        if c.get("studied"):
            cat_studied[cat] = cat_studied.get(cat, 0) + 1

    fig_cat = go.Figure()
    fig_cat.add_trace(go.Bar(
        name="Total",
        x=list(cat_counts.keys()),
        y=list(cat_counts.values()),
        marker_color="#1d3461",
    ))
    fig_cat.add_trace(go.Bar(
        name="Studied",
        x=list(cat_counts.keys()),
        y=[cat_studied.get(k, 0) for k in cat_counts],
        marker_color="#64ffda",
    ))
    layout = make_plotly_layout(st.session_state.dark_mode)
    fig_cat.update_layout(
        title="Cards per Category: Total vs Studied",
        barmode="group",
        height=320,
        **{k: v for k, v in layout.items() if k not in ("xaxis", "yaxis")},
    )
    st.plotly_chart(fig_cat, use_container_width=True)

    # ── Quiz score history ─────────────────────────────────────────────────────
    col_hist, col_diff2 = st.columns([2, 1])

    with col_hist:
        if history:
            fig_hist = go.Figure(go.Scatter(
                x=[h["date"] for h in history],
                y=[h["pct"] for h in history],
                mode="lines+markers",
                line=dict(color="#64ffda", width=2),
                marker=dict(size=8, color="#7b5ea7"),
                fill="tozeroy",
                fillcolor="rgba(100,255,218,0.07)",
            ))
            fig_hist.update_layout(
                title="Quiz Score History (%)",
                yaxis_range=[0, 100],
                height=280,
                **{k: v for k, v in layout.items() if k not in ("xaxis", "yaxis")},
            )
            st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.info("Complete at least one quiz to see score history here.")

    with col_diff2:
        diff_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        diff_studied = {"Easy": 0, "Medium": 0, "Hard": 0}
        for c in cards:
            d = c.get("difficulty", "Easy")
            diff_counts[d] += 1
            if c.get("studied"):
                diff_studied[d] += 1

        fig_d = go.Figure(go.Bar(
            x=list(diff_counts.keys()),
            y=list(diff_counts.values()),
            marker_color=["#22c55e", "#f59e0b", "#ef4444"],
            text=list(diff_counts.values()),
            textposition="outside",
        ))
        fig_d.update_layout(
            title="Cards by Difficulty",
            showlegend=False,
            height=280,
            **{k: v for k, v in layout.items() if k not in ("xaxis", "yaxis")},
        )
        st.plotly_chart(fig_d, use_container_width=True)

    # ── Quiz history table ─────────────────────────────────────────────────────
    if history:
        st.markdown("<div class='section-head'>Quiz History</div>", unsafe_allow_html=True)
        for i, h in enumerate(reversed(history[-10:])):
            pct_color = "#22c55e" if h["pct"] >= 70 else ("#f59e0b" if h["pct"] >= 40 else "#ef4444")
            st.markdown(
                f"<div class='list-card' style='display:flex;align-items:center;justify-content:space-between;'>"
                f"<div><div class='list-q'>Attempt #{len(history)-i}</div>"
                f"<div class='list-a'>{h['date']} &nbsp;·&nbsp; {h['score']}/{h['total']} correct</div></div>"
                f"<div style='font-family:Syne,sans-serif;font-size:1.5rem;font-weight:800;color:{pct_color};'>{h['pct']}%</div>"
                f"</div>",
                unsafe_allow_html=True,
            )

    render_footer()


# ═══════════════════════════════════════════════════════════════════════════════
# 14.  FOOTER
# ═══════════════════════════════════════════════════════════════════════════════

def render_footer() -> None:
    """Render the app footer."""
    st.markdown(
        "<div class='footer'>"
        "🃏 <strong>Flashcard Quiz App</strong> &nbsp;|&nbsp; "
        "Internship Portfolio Project &nbsp;|&nbsp; "
        "Built with <a href='https://streamlit.io' target='_blank'>Streamlit</a> &amp; Python 3<br>"
        "<span style='opacity:0.4;font-size:0.75rem;'>"
        "© 2024 · Your Name · "
        "<a href='https://github.com/yourusername/FlashcardQuizApp' target='_blank'>GitHub</a>"
        "</span>"
        "</div>",
        unsafe_allow_html=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# 15.  MAIN
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Application entry point: initialise state, inject CSS, route pages."""
    # 1. Initialise session state
    init_state()

    # 2. Inject theme CSS
    inject_css(dark=st.session_state.dark_mode)

    # 3. Render sidebar
    render_sidebar()

    # 4. Route to current page
    page = st.session_state.page

    if page == "Dashboard":
        page_dashboard()
    elif page == "Study Mode":
        page_study()
    elif page == "Quiz Mode":
        page_quiz()
    elif page == "Manage Cards":
        page_manage()
    elif page == "Favorites":
        page_favorites()
    elif page == "Statistics":
        page_statistics()


# ─── Entry point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    main()
