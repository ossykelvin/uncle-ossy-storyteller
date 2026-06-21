"""Supabase Auth wrappers.

Returns plain dicts so the UI never touches the SDK types directly.
A `session` dict carries: access_token, refresh_token, user_id, email.
"""
from core.supabase_client import anon_client


def _session_dict(resp) -> dict | None:
    session = getattr(resp, "session", None)
    user = getattr(resp, "user", None)
    if not session or not user:
        return None
    return {
        "access_token": session.access_token,
        "refresh_token": session.refresh_token,
        "user_id": user.id,
        "email": user.email,
    }


def sign_up(email: str, password: str) -> tuple[bool, str, dict | None]:
    email = (email or "").strip()
    if not email or not password:
        return False, "Email and password are required.", None
    if len(password) < 8:
        return False, "Password must be at least 8 characters.", None
    try:
        resp = anon_client().auth.sign_up({"email": email, "password": password})
    except Exception as exc:
        return False, f"Sign-up failed: {exc}", None
    session = _session_dict(resp)
    if session:
        return True, "Account created.", session
    # Email-confirmation flow: user created but no active session yet.
    return True, "Account created. Check your email to confirm, then log in.", None


def sign_in(email: str, password: str) -> tuple[bool, str, dict | None]:
    email = (email or "").strip()
    if not email or not password:
        return False, "Email and password are required.", None
    try:
        resp = anon_client().auth.sign_in_with_password({"email": email, "password": password})
    except Exception as exc:
        msg = str(exc)
        if "Email not confirmed" in msg:
            return False, "Please confirm your email before logging in.", None
        if "Invalid login" in msg:
            return False, "Invalid email or password.", None
        return False, f"Login failed: {msg}", None
    session = _session_dict(resp)
    if not session:
        return False, "Login failed: no session returned.", None
    return True, "Logged in.", session


def sign_out(access_token: str | None = None) -> None:
    try:
        anon_client().auth.sign_out()
    except Exception:
        pass
