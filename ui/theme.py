import streamlit as st
from core.config import THEME, APP_NAME


def apply_theme():
    st.set_page_config(page_title=APP_NAME, page_icon="📚", layout="wide")
    st.markdown(f"""
    <style>
    :root {{
        --primary: {THEME['primary']};
        --secondary: {THEME['secondary']};
        --background: {THEME['background']};
        --surface: {THEME['surface']};
        --accent: {THEME['accent']};
    }}
    .stApp {{ background: linear-gradient(135deg, {THEME['background']} 0%, #ffffff 55%, #eef2ff 100%); }}
    [data-testid="stSidebar"] {{ background: {THEME['primary']}; }}
    /* Sidebar: white for nav/labels/headings only — NOT form fields. */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] p, [data-testid="stSidebar"] label, [data-testid="stSidebar"] summary,
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    [data-testid="stSidebar"] button {{ color: #ffffff !important; }}
    /* Keep inputs legible: dark text on a white field. */
    [data-testid="stSidebar"] input, [data-testid="stSidebar"] textarea {{
        color: {THEME['primary']} !important; background: #ffffff !important;
    }}
    .hero-card {{
        background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']});
        color: white; padding: 24px 28px; border-radius: 20px; margin-bottom: 16px;
        box-shadow: 0 16px 40px rgba(13,27,61,.16);
    }}
    .hero-card h1 {{ color: white; margin: 0; }}
    .page-header {{ margin: 0 0 6px; }}
    .page-header h2 {{ color: {THEME['primary']}; margin: 0; font-size: 1.6rem; }}
    .page-header p {{ color: #475569; margin: 2px 0 0; }}
    div.stButton > button {{ border-radius: 12px; border: 1px solid {THEME['secondary']}; }}
    div.stButton > button[kind="primary"] {{ background:{THEME['secondary']}; color:white; }}
    </style>
    """, unsafe_allow_html=True)


def hero(title: str, subtitle: str):
    st.markdown(f"""
    <div class='hero-card'>
      <h1>{title}</h1>
      <p style='font-size:1.05rem;opacity:.92'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = "", status: str = ""):
    """Slim contextual header for working pages (keeps the big hero off them)."""
    chip = ""
    if status:
        chip = (f"<span style='background:rgba(37,99,235,.12);color:{THEME['secondary']};"
                f"font-size:.78rem;font-weight:600;padding:3px 12px;border-radius:999px;"
                f"margin-left:10px;vertical-align:middle'>{status}</span>")
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(f"<div class='page-header'><h2>{title}{chip}</h2>{sub}</div>", unsafe_allow_html=True)
