import streamlit as st
from core.config import DEFAULT_WORD_COUNT, DEFAULT_CHAPTER_COUNT
from core.storage import create_project
from agents.genre_style_curator import GENRES, STYLE_OPTIONS, SAFE_STYLE_PROFILES

PROJECT_TYPES = ["poem", "spoken word", "short story", "novella", "novel", "memoir", "non-fiction book", "essay collection"]


def render_new_project(username: str):
    st.subheader("Create New Project")
    with st.form("new_project_form"):
        title = st.text_input("Project title")
        project_type = st.selectbox("Project type", PROJECT_TYPES, index=4)
        fiction_type = st.radio("Fiction or non-fiction", ["fiction", "non-fiction"], horizontal=True)
        genre = st.selectbox("Genre", GENRES)
        theme = st.text_input("Theme", placeholder="e.g. betrayal, redemption, memory, faith, justice")
        style_pool = STYLE_OPTIONS.get(genre, [])
        style_label = st.selectbox("Author-inspired label or style label", style_pool + ["Custom / none"] if style_pool else ["Custom / none"])
        safe_style_profile = st.selectbox("Safe style profile", SAFE_STYLE_PROFILES)
        custom_style = st.text_area("Custom style notes", placeholder="Describe pacing, tone, sentence style, cultural flavour, dialogue, narrator voice...")
        chapter_count = st.number_input("Number of chapters/sections", min_value=1, max_value=200, value=DEFAULT_CHAPTER_COUNT)
        target_word_count = st.number_input("Target total word count", min_value=100, max_value=500000, value=DEFAULT_WORD_COUNT)
        seed_prompt = st.text_area("Your idea / brief / opening concept", height=160)
        submitted = st.form_submit_button("Create Project", type="primary")
    if submitted:
        if not title.strip():
            st.error("Project title is required.")
            return
        project = create_project(username, {
            "title": title,
            "project_type": project_type,
            "fiction_type": fiction_type,
            "genre": genre,
            "theme": theme,
            "style_label": style_label,
            "safe_style_profile": safe_style_profile,
            "custom_style": custom_style,
            "chapter_count": int(chapter_count),
            "target_word_count": int(target_word_count),
            "seed_prompt": seed_prompt,
        })
        st.session_state.current_project_id = project["id"]
        st.session_state.page = "Writing Studio"
        st.success("Project created.")
        st.rerun()
