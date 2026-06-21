import json
import streamlit as st
from agents.story_bible import SECTION_HELP
from core.storage import save_project
from core.utils import safe_json_loads


def render_story_bible(bundle: dict):
    st.subheader("Story Bible")
    st.caption("Edit characters, locations, plot points, timelines, and world rules manually. The Continuity Agent can also update this after approved chapters.")
    story_bible = bundle["story_bible"]
    tabs = st.tabs(list(story_bible.keys()) + ["Raw JSON"])
    keys = list(story_bible.keys())
    for tab, key in zip(tabs[:-1], keys):
        with tab:
            st.caption(SECTION_HELP.get(key, "Project memory section."))
            current = json.dumps(story_bible.get(key, []), indent=2, ensure_ascii=False)
            edited = st.text_area(key, current, height=260, key=f"bible_{key}")
            if st.button(f"Save {key}", key=f"save_{key}"):
                story_bible[key] = safe_json_loads(edited, story_bible.get(key, []))
                bundle["story_bible"] = story_bible
                save_project(bundle["project"]["id"], bundle)
                st.success(f"Saved {key}.")
    with tabs[-1]:
        raw = st.text_area("Full Story Bible JSON", json.dumps(story_bible, indent=2, ensure_ascii=False), height=500)
        if st.button("Save Full Story Bible"):
            bundle["story_bible"] = safe_json_loads(raw, story_bible)
            save_project(bundle["project"]["id"], bundle)
            st.success("Story Bible saved.")
