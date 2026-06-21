"""Supabase (Postgres) storage backend.

One row per project in the `projects` table:
  - denormalized columns (title/status/...) for cheap dashboard listing
  - a single `bundle` jsonb holding the full project bundle (source of truth)

Row-Level Security scopes every query to the logged-in user, so cross-user
access is impossible even if a project id leaks.

`project_dir()` still returns a local path: it is only used as a scratch area
for staging export files (md/docx/pdf/epub) before the browser downloads them.
"""
from pathlib import Path
from core.config import LOCAL_STORAGE_PATH, SUPABASE_SCHEMA
from core.utils import now_iso
from core.supabase_client import user_client
from core.storage_common import new_project_id, new_project_record, empty_bundle

TABLE = "projects"
_EXPORT_STAGING = LOCAL_STORAGE_PATH / "projects"

# Columns kept in sync with the bundle's project dict for fast listing.
_DENORM = ["title", "status", "project_type", "fiction_type", "genre", "chapter_count"]


def _table():
    return user_client().schema(SUPABASE_SCHEMA).table(TABLE)


def project_dir(project_id: str) -> Path:
    p = _EXPORT_STAGING / project_id
    p.mkdir(parents=True, exist_ok=True)
    (p / "exports").mkdir(exist_ok=True)
    return p


def _row(project: dict, bundle: dict) -> dict:
    row = {
        "id": project["id"],
        "owner": project["owner"],
        "updated_at": project.get("updated_at", now_iso()),
        "bundle": bundle,
    }
    for col in _DENORM:
        row[col] = project.get(col)
    return row


def list_projects(username: str) -> list[dict]:
    cols = "id,owner,updated_at," + ",".join(_DENORM)
    res = _table().select(cols).order("updated_at", desc=True).execute()
    return res.data or []


def create_project(username: str, payload: dict) -> dict:
    pid = new_project_id(payload.get("title", "untitled"))
    project = new_project_record(username, payload, pid)
    bundle = empty_bundle(project)
    _table().insert(_row(project, bundle)).execute()
    return project


def load_project_bundle(project_id: str) -> dict:
    res = _table().select("bundle").eq("id", project_id).limit(1).execute()
    if res.data:
        return res.data[0]["bundle"]
    return empty_bundle({})


def save_project(project_id: str, data: dict) -> None:
    project = data.get("project", {})
    project["updated_at"] = now_iso()
    # Merge the incoming sections into the stored bundle.
    bundle = load_project_bundle(project_id)
    bundle["project"] = project
    for name in ["outline", "story_bible", "chapters", "continuity_log", "qa_reports", "custom_style"]:
        if name in data:
            bundle[name] = data[name]
    _table().update(_row(project, bundle)).eq("id", project_id).execute()


def delete_project(project_id: str) -> None:
    _table().delete().eq("id", project_id).execute()


def user_owns_project(username: str, project_id: str) -> bool:
    if not username or not project_id:
        return False
    # RLS guarantees only the owner's rows are visible; a returned row == owned.
    res = _table().select("id").eq("id", project_id).limit(1).execute()
    return bool(res.data)
