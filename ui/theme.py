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
    .stApp {{ background: linear-gradient(135deg, {THEME['background']} 0%, #ffffff 45%, #eef2ff 100%); }}
    [data-testid="stSidebar"] {{ background: {THEME['primary']}; }}
    [data-testid="stSidebar"] * {{ color: white !important; }}
    .hero-card {{
        background: linear-gradient(135deg, {THEME['primary']}, {THEME['secondary']});
        color: white; padding: 28px; border-radius: 24px; margin-bottom: 18px;
        box-shadow: 0 20px 45px rgba(13,27,61,.18);
    }}
    .hero-card h1 {{ color: white; margin: 0; }}
    .studio-card {{
        background: rgba(255,255,255,.92); border: 1px solid rgba(37,99,235,.14);
        border-radius: 20px; padding: 18px; box-shadow: 0 12px 32px rgba(15,23,42,.06);
    }}
    .metric-card {{ background:white;border-radius:18px;padding:16px;border:1px solid #dbeafe; }}
    .warning-box {{background:#fff7ed;border-left:5px solid {THEME['warning']};padding:12px;border-radius:12px;}}
    .success-box {{background:#f0fdf4;border-left:5px solid {THEME['success']};padding:12px;border-radius:12px;}}
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
