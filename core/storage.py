"""Storage facade.

Auto-selects the backend per call:
  - Supabase Postgres when SUPABASE_URL + SUPABASE_ANON_KEY are configured
  - Local JSON files otherwise (default for local dev)

The public function names are unchanged, so the UI imports stay identical
regardless of which backend is active.
"""
from core.config import supabase_enabled
from core.storage_common import DEFAULT_STORY_BIBLE  # re-exported for compatibility
from core.supabase_client import set_access_token  # re-exported for app.py
import core.storage_json as _json_backend


def _backend():
    if supabase_enabled():
        import core.storage_supabase as _supabase_backend
        return _supabase_backend
    return _json_backend


def set_auth_context(access_token: str | None) -> None:
    """Bind the current request to a logged-in Supabase user (no-op for JSON)."""
    set_access_token(access_token)


def project_dir(project_id):
    return _backend().project_dir(project_id)


def list_projects(username: str) -> list[dict]:
    return _backend().list_projects(username)


def create_project(username: str, payload: dict) -> dict:
    return _backend().create_project(username, payload)


def load_project_bundle(project_id: str) -> dict:
    return _backend().load_project_bundle(project_id)


def save_project(project_id: str, data: dict) -> None:
    return _backend().save_project(project_id, data)


def delete_project(project_id: str) -> None:
    return _backend().delete_project(project_id)


def user_owns_project(username: str, project_id: str) -> bool:
    return _backend().user_owns_project(username, project_id)
