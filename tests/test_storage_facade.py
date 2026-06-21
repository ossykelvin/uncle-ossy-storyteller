"""Storage facade / JSON backend tests (Phase 5a).

Supabase is not configured in CI, so the facade resolves to the JSON backend.
We isolate PROJECTS_DIR to a temp dir so the real data/ is untouched.
"""
import pytest

import core.storage_json as sj
from core import storage
from core.storage_common import empty_bundle, new_project_record, new_project_id


@pytest.fixture
def projects_dir(tmp_path, monkeypatch):
    d = tmp_path / "projects"
    d.mkdir()
    monkeypatch.setattr(sj, "PROJECTS_DIR", d)
    return d


def test_facade_uses_json_backend_when_supabase_disabled(monkeypatch):
    monkeypatch.setattr("core.storage.supabase_enabled", lambda: False)
    assert storage._backend() is sj


def test_project_round_trip(projects_dir, monkeypatch):
    monkeypatch.setattr("core.storage.supabase_enabled", lambda: False)
    project = storage.create_project("alice", {"title": "My Book", "chapter_count": 2})
    pid = project["id"]

    assert storage.user_owns_project("alice", pid) is True
    assert storage.user_owns_project("bob", pid) is False

    projects = storage.list_projects("alice")
    assert any(p["id"] == pid for p in projects)
    assert storage.list_projects("bob") == []

    bundle = storage.load_project_bundle(pid)
    assert bundle["project"]["title"] == "My Book"
    assert bundle["story_bible"]["characters"] == []

    bundle["chapters"].append({"chapter_number": 1, "content": "Once upon a time"})
    storage.save_project(pid, bundle)
    assert storage.load_project_bundle(pid)["chapters"][0]["content"] == "Once upon a time"

    storage.delete_project(pid)
    assert storage.user_owns_project("alice", pid) is False


def test_common_builders_shape():
    pid = new_project_id("Hello World")
    project = new_project_record("alice", {"title": "Hello World"}, pid)
    assert project["owner"] == "alice"
    assert project["status"] == "idea"
    bundle = empty_bundle(project)
    assert set(bundle.keys()) == {
        "project", "outline", "story_bible", "chapters",
        "continuity_log", "qa_reports", "custom_style",
    }


def test_supabase_backend_imports():
    # Should import cleanly even with no credentials configured.
    import core.storage_supabase as ss
    assert hasattr(ss, "create_project")
