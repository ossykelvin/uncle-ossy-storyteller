import streamlit as st
from core.config import ensure_dirs, APP_NAME, DEFAULT_PROVIDER, supabase_enabled
from core.auth import authenticate, create_user, init_users, must_change_password, change_password
from ui.theme import apply_theme, hero
from ui.dashboard import render_dashboard
from ui.project_form import render_new_project
from ui.writing_studio import render_writing_studio
from ui.story_bible_ui import render_story_bible
from ui.export_ui import render_exports
from ui.settings_ui import render_settings
from core.storage import load_project_bundle, user_owns_project, set_auth_context

USE_SUPABASE = supabase_enabled()

ensure_dirs()
if not USE_SUPABASE:
    init_users()  # local backend bootstraps the admin user
apply_theme()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"
if "provider" not in st.session_state:
    st.session_state.provider = DEFAULT_PROVIDER


def _begin_session(username: str, display_name: str, session: dict | None = None):
    st.session_state.authenticated = True
    st.session_state.username = username          # owner key used by storage
    st.session_state.display_name = display_name  # shown in the sidebar
    if session:
        st.session_state.sb_access_token = session.get("access_token")
        st.session_state.sb_refresh_token = session.get("refresh_token")


def login_page_supabase():
    from core.auth_supabase import sign_in, sign_up
    hero(APP_NAME, "Your personal AI writing studio for novels, poems, spoken word, stories, and non-fiction.")
    tab1, tab2 = st.tabs(["Login", "Create Account"])
    with tab1:
        with st.form("login"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            ok, msg, session = sign_in(email, password)
            if ok and session:
                _begin_session(session["user_id"], session.get("email") or email, session)
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)
    with tab2:
        with st.form("create_user"):
            new_email = st.text_input("Email")
            new_password = st.text_input("Password", type="password")
            st.caption("At least 8 characters.")
            submitted = st.form_submit_button("Create Account")
        if submitted:
            ok, msg, session = sign_up(new_email, new_password)
            if ok and session:
                _begin_session(session["user_id"], session.get("email") or new_email, session)
                st.rerun()
            elif ok:
                st.success(msg)  # email-confirmation required
            else:
                st.error(msg)


def login_page_local():
    hero(APP_NAME, "Your personal AI writing studio for novels, poems, spoken word, stories, and non-fiction.")
    tab1, tab2 = st.tabs(["Login", "Create Local User"])
    with tab1:
        with st.form("login"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", type="primary")
        if submitted:
            if authenticate(username, password):
                _begin_session(username, username)
                st.success("Logged in.")
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with tab2:
        with st.form("create_user"):
            new_username = st.text_input("New username")
            new_email = st.text_input("Email (optional)")
            new_password = st.text_input("New password", type="password")
            st.caption("At least 8 characters, including a letter and a number.")
            submitted = st.form_submit_button("Create User")
        if submitted:
            ok, msg = create_user(new_username, new_password, new_email)
            st.success(msg) if ok else st.error(msg)


def login_page():
    if USE_SUPABASE:
        login_page_supabase()
    else:
        login_page_local()


def force_password_change_page():
    hero(APP_NAME, "Set a new password to continue.")
    st.warning("Your account is still using the default password. Please set a new one before continuing.")
    with st.form("force_change"):
        current = st.text_input("Current password", type="password")
        new1 = st.text_input("New password", type="password")
        new2 = st.text_input("Confirm new password", type="password")
        st.caption("At least 8 characters, including a letter and a number.")
        submitted = st.form_submit_button("Update Password", type="primary")
    if submitted:
        if new1 != new2:
            st.error("New passwords do not match.")
            return
        ok, msg = change_password(st.session_state.username, current, new1)
        if ok:
            st.success(msg)
            st.rerun()
        else:
            st.error(msg)


if not st.session_state.authenticated:
    login_page()
    st.stop()

# Bind this request to the logged-in Supabase user so RLS applies (no-op for local).
set_auth_context(st.session_state.get("sb_access_token"))

if not USE_SUPABASE and must_change_password(st.session_state.username):
    force_password_change_page()
    st.stop()

with st.sidebar:
    st.markdown(f"# 📚 {APP_NAME}")
    st.caption(f"Logged in as {st.session_state.get('display_name', st.session_state.username)}")
    selected = st.radio("Navigate", ["Dashboard", "New Project", "Writing Studio", "Story Bible", "Export Centre", "Settings"], index=["Dashboard", "New Project", "Writing Studio", "Story Bible", "Export Centre", "Settings"].index(st.session_state.page))
    st.session_state.page = selected
    if st.button("Logout"):
        if USE_SUPABASE:
            from core.auth_supabase import sign_out
            sign_out(st.session_state.get("sb_access_token"))
        for k in ["authenticated", "username", "display_name", "current_project_id", "sb_access_token", "sb_refresh_token"]:
            st.session_state.pop(k, None)
        st.rerun()
    if USE_SUPABASE:
        st.caption("Forgot your password? Use the reset link from your Supabase login email.")
    else:
        with st.expander("Change password"):
            with st.form("sidebar_change_pw"):
                cur_pw = st.text_input("Current", type="password")
                new_pw = st.text_input("New", type="password")
                cfm_pw = st.text_input("Confirm", type="password")
                if st.form_submit_button("Update"):
                    if new_pw != cfm_pw:
                        st.error("New passwords do not match.")
                    else:
                        ok, msg = change_password(st.session_state.username, cur_pw, new_pw)
                        st.success(msg) if ok else st.error(msg)

page = st.session_state.page
if page == "Dashboard":
    hero(APP_NAME, "Plan, write, rewrite, approve, remember, and export your stories from one beautiful dashboard.")
    render_dashboard(st.session_state.username)
elif page == "New Project":
    render_new_project(st.session_state.username)
elif page == "Writing Studio":
    pid = st.session_state.get("current_project_id")
    if pid and not user_owns_project(st.session_state.username, pid):
        st.error("You do not have access to this project.")
        st.session_state.pop("current_project_id", None)
    else:
        render_writing_studio(st.session_state.provider)
elif page == "Story Bible":
    pid = st.session_state.get("current_project_id")
    if not pid:
        st.warning("Open a project first from the Dashboard.")
    elif not user_owns_project(st.session_state.username, pid):
        st.error("You do not have access to this project.")
    else:
        render_story_bible(load_project_bundle(pid))
elif page == "Export Centre":
    pid = st.session_state.get("current_project_id")
    if not pid:
        st.warning("Open a project first from the Dashboard.")
    elif not user_owns_project(st.session_state.username, pid):
        st.error("You do not have access to this project.")
    else:
        render_exports(load_project_bundle(pid), st.session_state.provider)
elif page == "Settings":
    render_settings()
