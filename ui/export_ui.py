import streamlit as st
from core.exports import export_markdown, export_html, export_docx, export_pdf, export_epub
from agents.cover_marketing_agent import generate_back_cover, generate_cover_prompt
from core.storage import save_project


def _download(path):
    st.download_button(f"Download {path.suffix.upper().strip('.')}", data=path.read_bytes(), file_name=path.name)


def render_exports(bundle: dict, provider: str):
    st.subheader("Export Centre")
    c1, c2, c3, c4, c5 = st.columns(5)
    if c1.button("Export MD"):
        _download(export_markdown(bundle))
    if c2.button("Export HTML"):
        _download(export_html(bundle))
    if c3.button("Export DOCX"):
        _download(export_docx(bundle))
    if c4.button("Export PDF"):
        _download(export_pdf(bundle))
    if c5.button("Export EPUB"):
        _download(export_epub(bundle))

    st.divider()
    st.subheader("Publishing Assets")
    if st.button("Generate Back-Cover Blurb"):
        with st.spinner("Creating blurb..."):
            blurb = generate_back_cover(bundle["project"], bundle["outline"].get("content", ""), bundle["story_bible"], provider)
            bundle["project"]["back_cover_blurb"] = blurb
            save_project(bundle["project"]["id"], bundle)
            st.session_state.generated_blurb = blurb
    if "generated_blurb" in st.session_state:
        st.text_area("Back-cover blurb", st.session_state.generated_blurb, height=180)
    elif bundle["project"].get("back_cover_blurb"):
        st.text_area("Back-cover blurb", bundle["project"].get("back_cover_blurb"), height=180)

    if st.button("Generate Book Cover Prompt"):
        with st.spinner("Creating cover prompt..."):
            prompt = generate_cover_prompt(bundle["project"], bundle["outline"].get("content", ""), bundle["story_bible"], provider)
            bundle["project"]["book_cover_prompt"] = prompt
            save_project(bundle["project"]["id"], bundle)
            st.session_state.cover_prompt = prompt
    if "cover_prompt" in st.session_state:
        st.text_area("Book cover prompt", st.session_state.cover_prompt, height=220)
    elif bundle["project"].get("book_cover_prompt"):
        st.text_area("Book cover prompt", bundle["project"].get("book_cover_prompt"), height=220)
