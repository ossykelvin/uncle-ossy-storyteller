import json
import pandas as pd
import streamlit as st
from agents.story_bible import SECTION_HELP
from core.storage import save_project

# Guided starter columns so an empty section isn't a blank grid.
SECTION_COLUMNS = {
    "characters": ["name", "role", "notes"],
    "locations": ["name", "notes"],
    "timeline": ["when", "event"],
    "plot_points": ["point", "notes"],
    "themes": ["theme"],
    "world_rules": ["rule", "notes"],
    "objects": ["name", "notes"],
    "relationships": ["from", "to", "type", "notes"],
    "unresolved_threads": ["thread", "status"],
    "chapter_summaries": ["chapter", "summary"],
    "glossary": ["term", "definition"],
}


def _is_scalar_list(items: list) -> bool:
    return bool(items) and all(isinstance(x, (str, int, float, bool)) for x in items)


def _is_flat_dict_list(items: list) -> bool:
    return bool(items) and all(
        isinstance(x, dict) and all(not isinstance(v, (dict, list)) for v in x.values())
        for x in items
    )


def _is_blank(v) -> bool:
    try:
        if pd.isna(v):  # catches None, nan, and pandas NA
            return True
    except (TypeError, ValueError):
        pass
    return str(v).strip() == ""


def _records_from_df(df: pd.DataFrame) -> list[dict]:
    records = []
    for row in df.to_dict("records"):
        cleaned = {k: ("" if _is_blank(v) else v) for k, v in row.items()}
        if any(str(v).strip() for v in cleaned.values()):  # skip fully-empty rows
            records.append(cleaned)
    return records


def _render_section(story_bible: dict, key: str, project_id: str, bundle: dict):
    st.caption(SECTION_HELP.get(key, "Project memory section."))
    items = story_bible.get(key, [])
    scalar_col = SECTION_COLUMNS.get(key, ["value"])[0]

    if items and not (_is_scalar_list(items) or _is_flat_dict_list(items)):
        # Irregular / nested data: safe JSON editor WITH validation (no silent loss).
        text = st.text_area(key, json.dumps(items, indent=2, ensure_ascii=False), height=260, key=f"bible_json_{key}")
        if st.button(f"Save {key}", key=f"save_{key}"):
            try:
                story_bible[key] = json.loads(text)
            except json.JSONDecodeError as exc:
                st.error(f"Not saved — invalid JSON: {exc.msg} (line {exc.lineno}). Fix it and try again.")
                return
            bundle["story_bible"] = story_bible
            save_project(project_id, bundle)
            st.success(f"Saved {key}.")
        return

    # Flat data → spreadsheet-style editor.
    scalars = _is_scalar_list(items)
    if scalars:
        df = pd.DataFrame({scalar_col: items})
    elif items:
        df = pd.DataFrame(items)
    else:
        df = pd.DataFrame(columns=SECTION_COLUMNS.get(key, ["value"]))

    edited = st.data_editor(df, num_rows="dynamic", use_container_width=True, key=f"bible_editor_{key}")
    if st.button(f"Save {key}", key=f"save_{key}"):
        if scalars:
            values = [str(v).strip() for v in edited[scalar_col].tolist() if not _is_blank(v)]
            story_bible[key] = values
        else:
            story_bible[key] = _records_from_df(edited)
        bundle["story_bible"] = story_bible
        save_project(project_id, bundle)
        st.success(f"Saved {key}.")


def render_story_bible(bundle: dict):
    st.subheader("Story Bible")
    st.caption("Edit characters, locations, plot points, timelines, and world rules in the grids below. The Continuity Agent can also update this after approved chapters.")
    story_bible = bundle["story_bible"]
    project_id = bundle["project"]["id"]
    keys = list(story_bible.keys())
    tabs = st.tabs(keys + ["Raw JSON"])
    for tab, key in zip(tabs[:-1], keys):
        with tab:
            _render_section(story_bible, key, project_id, bundle)
    with tabs[-1]:
        st.caption("Advanced: edit the entire Story Bible as JSON.")
        raw = st.text_area("Full Story Bible JSON", json.dumps(story_bible, indent=2, ensure_ascii=False), height=500)
        if st.button("Save Full Story Bible"):
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError as exc:
                st.error(f"Not saved — invalid JSON: {exc.msg} (line {exc.lineno}).")
                return
            bundle["story_bible"] = parsed
            save_project(project_id, bundle)
            st.success("Story Bible saved.")
