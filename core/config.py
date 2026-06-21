import os
from pathlib import Path
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = ROOT_DIR / ".env.local"
load_dotenv(ENV_PATH)


def _secret_value(key: str):
    """Read from Streamlit secrets when available, otherwise environment variables.

    Streamlit Cloud often uses st.secrets instead of a checked-in .env.local file.
    This helper keeps local development and cloud deployment working the same way.
    """
    try:
        import streamlit as st  # imported lazily so non-Streamlit tools still work
        if hasattr(st, "secrets") and key in st.secrets:
            return str(st.secrets[key])
    except Exception:
        pass
    return os.getenv(key)


def env(key: str, default: str = "") -> str:
    value = _secret_value(key)
    if value is None or str(value).strip() == "":
        return default
    return str(value)


def env_bool(key: str, default: bool = False) -> bool:
    value = _secret_value(key)
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


def env_int(key: str, default: int) -> int:
    value = _secret_value(key)
    if value is None:
        return default
    try:
        return int(str(value))
    except ValueError:
        return default


APP_NAME = env("APP_NAME", "Uncle Ossy StoryTeller")
APP_PORT = env_int("APP_PORT", 8443)
DEFAULT_PROVIDER = env("DEFAULT_PROVIDER", "openrouter")
FALLBACK_PROVIDER = env("FALLBACK_PROVIDER", "gemini")

# ── Supabase (optional) ────────────────────────────────────────────────
# When SUPABASE_URL and SUPABASE_ANON_KEY are set, the app switches to
# Supabase Auth + Postgres storage. Otherwise it uses local login + JSON files.
SUPABASE_URL = env("SUPABASE_URL", "")
# Accepts either the legacy anon JWT or the new sb_publishable_... key.
SUPABASE_ANON_KEY = env("SUPABASE_ANON_KEY", "") or env("SUPABASE_PUBLISHABLE_KEY", "")
# Tables live in this Postgres schema (must be in PostgREST "Exposed schemas").
SUPABASE_SCHEMA = env("SUPABASE_SCHEMA", "StoryTeller")


def supabase_enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_ANON_KEY)

# ── Brevo transactional email (optional) ───────────────────────────────
BREVO_API_KEY = env("BREVO_API_KEY", "")
BREVO_SENDER_EMAIL = env("BREVO_SENDER_EMAIL", "")
BREVO_SENDER_NAME = env("BREVO_SENDER_NAME", APP_NAME)
# Where new-signup admin alerts are sent (defaults to the sender address).
SIGNUP_ALERT_EMAIL = env("BREVO_ADMIN_EMAIL", "") or BREVO_SENDER_EMAIL


def brevo_enabled() -> bool:
    return bool(BREVO_API_KEY and BREVO_SENDER_EMAIL)

LOCAL_STORAGE_PATH = Path(env("LOCAL_STORAGE_PATH", "./data"))
EXPORT_STORAGE_PATH = Path(env("EXPORT_STORAGE_PATH", "./data/exports"))
CUSTOM_STYLE_PATH = Path(env("CUSTOM_STYLE_PATH", "./data/custom_styles"))

DEFAULT_WORD_COUNT = env_int("DEFAULT_WORD_COUNT", 3000)
DEFAULT_CHAPTER_COUNT = env_int("DEFAULT_CHAPTER_COUNT", 12)
REQUIRE_CHAPTER_APPROVAL = env_bool("REQUIRE_CHAPTER_APPROVAL", True)
ENABLE_CONTINUITY_WARNINGS = env_bool("ENABLE_CONTINUITY_WARNINGS", True)
ENABLE_AUTO_SUMMARY = env_bool("ENABLE_AUTO_SUMMARY", True)

THEME = {
    "primary": env("THEME_PRIMARY", "#0D1B3D"),
    "secondary": env("THEME_SECONDARY", "#2563EB"),
    "background": env("THEME_BACKGROUND", "#F2F4F7"),
    "surface": env("THEME_SURFACE", "#FFFFFF"),
    "accent": env("THEME_ACCENT", "#7C3AED"),
    "success": env("THEME_SUCCESS", "#16A34A"),
    "warning": env("THEME_WARNING", "#F59E0B"),
    "danger": env("THEME_DANGER", "#DC2626"),
}

MODEL_KEYS = ["writing", "outline", "editing", "research", "continuity", "qa", "marketing", "export"]


def get_model(provider: str, purpose: str) -> str:
    prefix = provider.upper()
    specific = env(f"{prefix}_{purpose.upper()}_MODEL", "")
    if specific:
        return specific
    return env(f"{prefix}_WRITING_MODEL", "")


def ensure_dirs() -> None:
    for path in [LOCAL_STORAGE_PATH, EXPORT_STORAGE_PATH, CUSTOM_STYLE_PATH, LOCAL_STORAGE_PATH / "projects"]:
        path.mkdir(parents=True, exist_ok=True)
