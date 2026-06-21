"""Shared storage helpers used by both the JSON and Supabase backends.

Keeping the project/bundle construction here guarantees the two backends
produce byte-for-byte identical data shapes, so the UI never has to care
which one is active.
"""
from core.utils import slugify, now_iso

DEFAULT_STORY_BIBLE = {
    "characters": [],
    "locations": [],
    "timeline": [],
    "plot_points": [],
    "themes": [],
    "world_rules": [],
    "objects": [],
    "relationships": [],
    "unresolved_threads": [],
    "chapter_summaries": [],
    "glossary": [],
}


def new_project_id(title: str) -> str:
    slug = slugify(title or "untitled")
    return f"{slug}-{now_iso().replace(':', '').replace('-', '')[:15]}"


def new_project_record(username: str, payload: dict, project_id: str) -> dict:
    """Build the canonical project.json dict for a freshly created project."""
    return {
        "id": project_id,
        "owner": username,
        "title": payload.get("title", "Untitled Project"),
        "project_type": payload.get("project_type", "novel"),
        "fiction_type": payload.get("fiction_type", "fiction"),
        "genre": payload.get("genre", "Fantasy"),
        "theme": payload.get("theme", ""),
        "style_label": payload.get("style_label", ""),
        "safe_style_profile": payload.get("safe_style_profile", ""),
        "custom_style": payload.get("custom_style", ""),
        "target_word_count": payload.get("target_word_count", 3000),
        "chapter_count": payload.get("chapter_count", 1),
        "current_chapter": 1,
        "status": "idea",
        "seed_prompt": payload.get("seed_prompt", ""),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }


def empty_bundle(project: dict) -> dict:
    """The full project bundle as returned by load_project_bundle()."""
    return {
        "project": project,
        "outline": {"content": "", "approved": False, "created_at": ""},
        "story_bible": dict(DEFAULT_STORY_BIBLE),
        "chapters": [],
        "continuity_log": [],
        "qa_reports": [],
        "custom_style": {"profiles": []},
    }
