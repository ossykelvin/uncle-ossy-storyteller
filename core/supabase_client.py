"""Supabase client factory.

The access token is held in a ContextVar so each Streamlit script-run thread
gets its own user-scoped token — never shared across sessions. Postgres queries
made through `user_client()` run as the logged-in user, so Row-Level Security
(owner = auth.uid()) is enforced server-side.

We build a fresh client per call rather than caching one: setting a per-user JWT
on a shared client would let concurrent sessions clobber each other's auth header.
At this scale the construction cost is negligible.
"""
import contextvars
from core.config import SUPABASE_URL, SUPABASE_ANON_KEY, supabase_enabled

_access_token: contextvars.ContextVar = contextvars.ContextVar("sb_access_token", default=None)


def is_configured() -> bool:
    return supabase_enabled()


def set_access_token(token: str | None) -> None:
    _access_token.set(token)


def get_access_token() -> str | None:
    return _access_token.get()


def _make_client():
    from supabase import create_client
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY)


def anon_client():
    """Client using the anon key (used for sign-up / sign-in)."""
    return _make_client()


def user_client():
    """Client whose PostgREST calls carry the current user's JWT (for RLS)."""
    client = _make_client()
    token = get_access_token()
    if token:
        client.postgrest.auth(token)
    return client
