import streamlit as st
from core.storage import list_projects


def render_dashboard(username: str):
    projects = list_projects(username)
    cols = st.columns(4)
    cols[0].metric("Projects", len(projects))
    cols[1].metric("Drafting", sum(1 for p in projects if p.get("status") == "drafting"))
    cols[2].metric("Completed", sum(1 for p in projects if p.get("status") == "completed"))
    cols[3].metric("This is", "MVP")
    st.subheader("Your Projects")
    if not projects:
        st.info("No projects yet. Create your first story, poem, spoken word piece, or book from the New Project page.")
        return
    for p in projects:
        with st.container(border=True):
            c1, c2, c3, c4 = st.columns([3, 1.5, 1.5, 1])
            c1.markdown(f"### {p.get('title')}")
            c1.caption(f"{p.get('project_type')} • {p.get('genre')} • {p.get('fiction_type')}")
            c2.write(f"Status: **{p.get('status')}**")
            c3.write(f"Chapters: **{p.get('chapter_count')}**")
            if c4.button("Open", key=f"open_{p.get('id')}"):
                st.session_state.current_project_id = p.get("id")
                st.session_state.page = "Writing Studio"
                st.rerun()
