import json
import re
import streamlit as st
from core.storage import load_project_bundle, save_project
from core.utils import now_iso, safe_json_loads
from agents.outline_agent import generate_outline
from agents.chapter_writer import write_chapter, rewrite_chapter
from agents.continuity_memory import summarize_chapter, check_contradictions, update_story_bible
from agents.project_manager import can_generate_next, next_chapter_number
from agents.story_qa_agent import qa_project
from core.ai_client import AIClientError, provider_status


def _chapter_title(content: str, chapter_number: int) -> str:
    first = content.strip().splitlines()[0] if content.strip() else f"Chapter {chapter_number}"
    first = re.sub(r"^#+\s*", "", first).strip()
    return first[:120]


def render_writing_studio(provider: str):
    project_id = st.session_state.get("current_project_id")
    if not project_id:
        st.warning("Open or create a project first.")
        return
    bundle = load_project_bundle(project_id)
    project = bundle["project"]
    st.markdown(f"## {project.get('title')}")
    st.caption(f"{project.get('project_type')} • {project.get('genre')} • {project.get('safe_style_profile')}")
    status = provider_status()
    if not status.get(f"{provider}_has_key", False):
        st.warning(f"{provider.title()} is selected but its API key is not configured. Add it in .env.local or Streamlit secrets, or choose another provider in Settings.")
    tabs = st.tabs(["Outline", "Current Chapter", "Review & Approval", "Continuity", "Story QA"])

    with tabs[0]:
        st.subheader("Outline")
        if not bundle["outline"].get("content"):
            st.info("Generate a full outline or paste your own.")
        outline_text = st.text_area("Outline", bundle["outline"].get("content", ""), height=420)
        c1, c2, c3 = st.columns(3)
        if c1.button("Generate Outline", type="primary"):
            with st.spinner("Generating outline..."):
                try:
                    outline_text = generate_outline(project, provider)
                except Exception as exc:
                    st.error("Outline generation failed, but the app did not crash. Check provider API key/model settings or enable offline fallback.")
                    with st.expander("Technical details"):
                        st.code(str(exc))
                    return
                bundle["outline"] = {"content": outline_text, "approved": False, "created_at": now_iso()}
                project["status"] = "outline"
                save_project(project_id, bundle)
                st.rerun()
        if c2.button("Save Outline"):
            bundle["outline"]["content"] = outline_text
            save_project(project_id, bundle)
            st.success("Outline saved.")
        if c3.button("Approve Outline"):
            bundle["outline"]["content"] = outline_text
            bundle["outline"]["approved"] = True
            project["status"] = "drafting"
            save_project(project_id, bundle)
            st.success("Outline approved.")

    with tabs[1]:
        st.subheader("Chapter Writer")
        ok, msg = can_generate_next(project, bundle["chapters"])
        st.caption(msg)
        chapter_instruction = st.text_area("Instruction for the next chapter", placeholder="Optional: add what should happen, tone, POV, or scene focus.")
        if st.button("Generate Next Chapter", disabled=not ok, type="primary"):
            with st.spinner("Writing chapter..."):
                n = next_chapter_number(bundle["chapters"])
                try:
                    content = write_chapter(project, bundle["outline"].get("content", ""), bundle["story_bible"], bundle["chapters"], n, chapter_instruction, provider)
                except Exception as exc:
                    st.error("Chapter generation failed, but the app did not crash. Check provider API key/model settings or enable offline fallback.")
                    with st.expander("Technical details"):
                        st.code(str(exc))
                    return
                warnings = ""
                try:
                    warnings = check_contradictions(project, bundle["story_bible"], bundle["chapters"], content, provider)
                except Exception as exc:
                    warnings = f"Continuity check failed: {exc}"
                bundle["chapters"].append({
                    "chapter_number": n,
                    "title": _chapter_title(content, n),
                    "status": "draft",
                    "target_word_count": int(project.get("target_word_count", 3000)) // max(1, int(project.get("chapter_count", 1))),
                    "content": content,
                    "summary": "",
                    "continuity_warnings": warnings,
                    "created_at": now_iso(),
                    "approved_at": "",
                })
                save_project(project_id, bundle)
                st.rerun()

        drafts = [c for c in bundle["chapters"] if c.get("status") == "draft"]
        if drafts:
            draft = drafts[-1]
            st.text_area("Draft chapter", draft.get("content", ""), height=520, key="draft_content_view")
            tone = st.text_input("Rewrite tone", placeholder="e.g. darker, more lyrical, faster-paced, more humorous, more suspenseful")
            if st.button("Rewrite Draft in Tone"):
                if not tone.strip():
                    st.error("Enter a tone first.")
                else:
                    with st.spinner("Rewriting..."):
                        try:
                            draft["content"] = rewrite_chapter(project, draft.get("content", ""), tone, provider)
                        except Exception as exc:
                            st.error("Rewrite failed, but the app did not crash. Check provider API key/model settings or enable offline fallback.")
                            with st.expander("Technical details"):
                                st.code(str(exc))
                            return
                        draft["title"] = _chapter_title(draft["content"], draft["chapter_number"])
                        save_project(project_id, bundle)
                        st.rerun()
        else:
            st.write("No active draft chapter.")

    with tabs[2]:
        st.subheader("Review & Approval")
        for idx, c in enumerate(sorted(bundle["chapters"], key=lambda x: x.get("chapter_number", 0))):
            with st.expander(f"Chapter {c.get('chapter_number')}: {c.get('title', '')} — {c.get('status')}", expanded=c.get("status") == "draft"):
                edited = st.text_area("Content", c.get("content", ""), height=420, key=f"chapter_edit_{c.get('chapter_number')}")
                c["content"] = edited
                if c.get("continuity_warnings"):
                    st.markdown("#### Continuity Warnings")
                    st.warning(c.get("continuity_warnings"))
                cc1, cc2 = st.columns(2)
                if cc1.button("Save Changes", key=f"save_ch_{c.get('chapter_number')}"):
                    save_project(project_id, bundle)
                    st.success("Chapter saved.")
                if cc2.button("Approve Chapter", key=f"approve_ch_{c.get('chapter_number')}", disabled=c.get("status") == "approved"):
                    with st.spinner("Approving, summarising, and updating memory..."):
                        c["status"] = "approved"
                        c["approved_at"] = now_iso()
                        try:
                            c["summary"] = summarize_chapter(project, c.get("chapter_number"), c.get("content", ""), provider)
                            update_json = update_story_bible(project, bundle["story_bible"], c.get("chapter_number"), c["summary"], provider)
                            bundle["story_bible"] = safe_json_loads(update_json, bundle["story_bible"])
                        except Exception as exc:
                            st.error("Approval memory update failed, but the app did not crash. The chapter was left as draft.")
                            with st.expander("Technical details"):
                                st.code(str(exc))
                            c["status"] = "draft"
                            c["approved_at"] = ""
                            return
                        project["current_chapter"] = min(int(project.get("chapter_count", 1)), c.get("chapter_number") + 1)
                        if c.get("chapter_number") >= int(project.get("chapter_count", 1)):
                            project["status"] = "completed"
                        else:
                            project["status"] = "drafting"
                        save_project(project_id, bundle)
                        st.success("Chapter approved and Story Bible updated.")
                        st.rerun()

    with tabs[3]:
        st.subheader("Continuity Log")
        for c in bundle["chapters"]:
            st.markdown(f"### Chapter {c.get('chapter_number')}: {c.get('title', '')}")
            st.write("**Summary:**")
            st.write(c.get("summary") or "Not approved/summarised yet.")
            if c.get("continuity_warnings"):
                st.write("**Warnings:**")
                st.warning(c.get("continuity_warnings"))

    with tabs[4]:
        st.subheader("Story QA")
        if st.button("Run Story QA Report"):
            with st.spinner("Running QA review..."):
                try:
                    report = qa_project(project, bundle["outline"].get("content", ""), bundle["story_bible"], bundle["chapters"], provider)
                except Exception as exc:
                    st.error("Story QA failed, but the app did not crash. Check provider API key/model settings or enable offline fallback.")
                    with st.expander("Technical details"):
                        st.code(str(exc))
                    return
                bundle["qa_reports"].append({"created_at": now_iso(), "report": report})
                save_project(project_id, bundle)
                st.session_state.last_qa_report = report
        if st.session_state.get("last_qa_report"):
            st.markdown(st.session_state.last_qa_report)
        for r in bundle.get("qa_reports", [])[-3:]:
            with st.expander(f"QA Report {r.get('created_at')}"):
                st.markdown(r.get("report", ""))

    with st.expander("Advanced · Project data (debug)"):
        st.json(bundle)
