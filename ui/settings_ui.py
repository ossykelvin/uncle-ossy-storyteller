import streamlit as st
from core.config import env, MODEL_KEYS, DEFAULT_PROVIDER, FALLBACK_PROVIDER
from core.ai_client import provider_status
from agents.settings_agent import PROVIDER_OPTIONS


def render_settings():
    st.subheader("Settings")
    st.info("This MVP reads settings from `.env.local`. Edit that file to persist changes. Runtime selections below apply to the current session.")
    st.session_state.provider = st.selectbox("Provider", PROVIDER_OPTIONS, index=PROVIDER_OPTIONS.index(st.session_state.get("provider", DEFAULT_PROVIDER)))
    st.session_state.fallback_provider = st.selectbox("Fallback provider", PROVIDER_OPTIONS, index=PROVIDER_OPTIONS.index(st.session_state.get("fallback_provider", FALLBACK_PROVIDER)))
    st.write("### Provider health")
    status = provider_status()
    st.write({
        "default_provider": status["default_provider"],
        "fallback_provider": status["fallback_provider"],
        "openrouter_api_key_configured": status["openrouter_has_key"],
        "gemini_api_key_configured": status["gemini_has_key"],
    })
    if not status["openrouter_has_key"] and not status["gemini_has_key"]:
        st.warning("No AI provider API key is configured yet. Add OPENROUTER_API_KEY or GEMINI_API_KEY in .env.local locally, or Streamlit secrets in Streamlit Cloud.")
    st.write("### Current model values from `.env.local` / Streamlit secrets")
    rows = []
    for purpose in MODEL_KEYS:
        rows.append({
            "purpose": purpose,
            "openrouter": env(f"OPENROUTER_{purpose.upper()}_MODEL", ""),
            "gemini": env(f"GEMINI_{purpose.upper()}_MODEL", ""),
        })
    st.dataframe(rows, use_container_width=True)
    st.write("### Offline fallback")
    st.write({"ENABLE_OFFLINE_FALLBACK": env("ENABLE_OFFLINE_FALLBACK", "true")})
    st.caption("When enabled, the app shows placeholder output instead of crashing while provider settings are being fixed.")
    st.write("### Storage")
    st.code("LOCAL_STORAGE_PATH, EXPORT_STORAGE_PATH and CUSTOM_STYLE_PATH are controlled in .env.local")
