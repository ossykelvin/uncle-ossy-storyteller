"""Local JSON-file storage backend (default; used for local dev and as a fallback).

This preserves the original on-disk layout: data/projects/<id>/*.json
"""
import json
import shutil
from pathlib import Path
from typing import Any
from core.config import LOCAL_STORAGE_PATH, ensure_dirs
from core.utils import now_iso
from core.storage_common import DEFAULT_STORY_BIBLE, new_project_id, new_project_record, empty_bundle

PROJECTS_DIR = LOCAL_STORAGE_PATH / "projects"

_SECTION_FILES = ["outline", "story_bible", "chapters", "continuity_log", "qa_reports", "custom_style"]


def read_json(path: Path, fallback: Any):
    if not path.exists():
        return fallback
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def project_dir(project_id: str) -> Path:
    return PROJECTS_DIR / project_id


def list_projects(username: str) -> list[dict]:
    ensure_dirs()
    projects = []
    for project_file in PROJECTS_DIR.glob("*/project.json"):
        project = read_json(project_file, {})
        if project and project.get("owner") == username:
            project["_path"] = str(project_file.parent)
            projects.append(project)
    return sorted(projects, key=lambda p: p.get("updated_at", ""), reverse=True)


def create_project(username: str, payload: dict) -> dict:
    ensure_dirs()
    pid = new_project_id(payload.get("title", "untitled"))
    pdir = PROJECTS_DIR / pid
    pdir.mkdir(parents=True, exist_ok=True)
    project = new_project_record(username, payload, pid)
    bundle = empty_bundle(project)
    write_json(pdir / "project.json", project)
    write_json(pdir / "outline.json", bundle["outline"])
    write_json(pdir / "story_bible.json", bundle["story_bible"])
    write_json(pdir / "chapters.json", bundle["chapters"])
    write_json(pdir / "continuity_log.json", bundle["continuity_log"])
    write_json(pdir / "qa_reports.json", bundle["qa_reports"])
    write_json(pdir / "custom_style.json", bundle["custom_style"])
    (pdir / "exports").mkdir(exist_ok=True)
    (pdir / "assets").mkdir(exist_ok=True)
    return project


def load_project_bundle(project_id: str) -> dict:
    p = project_dir(project_id)
    return {
        "project": read_json(p / "project.json", {}),
        "outline": read_json(p / "outline.json", {"content": "", "approved": False}),
        "story_bible": read_json(p / "story_bible.json", DEFAULT_STORY_BIBLE),
        "chapters": read_json(p / "chapters.json", []),
        "continuity_log": read_json(p / "continuity_log.json", []),
        "qa_reports": read_json(p / "qa_reports.json", []),
        "custom_style": read_json(p / "custom_style.json", {"profiles": []}),
    }


def save_project(project_id: str, data: dict) -> None:
    p = project_dir(project_id)
    project = data.get("project", {})
    project["updated_at"] = now_iso()
    write_json(p / "project.json", project)
    for name in _SECTION_FILES:
        if name in data:
            write_json(p / f"{name}.json", data[name])


def delete_project(project_id: str) -> None:
    p = project_dir(project_id)
    if p.exists():
        shutil.rmtree(p)


def user_owns_project(username: str, project_id: str) -> bool:
    if not username or not project_id:
        return False
    project = read_json(project_dir(project_id) / "project.json", {})
    return project.get("owner") == username
