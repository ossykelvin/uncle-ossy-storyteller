"""Auth hardening tests (Phase 2).

Run: .venv\\Scripts\\python -m pytest tests/test_auth.py -q
Uses an isolated temp users file so the real data/ directory is never touched.
"""
import hashlib
import json

import pytest

import core.auth as auth


@pytest.fixture
def store(tmp_path, monkeypatch):
    users_file = tmp_path / "users.json"
    monkeypatch.setattr(auth, "USERS_FILE", users_file)
    return users_file


def _seed_legacy_admin(users_file, password="change-me"):
    legacy = hashlib.sha256(f"local-mvp:{password}".encode()).hexdigest()
    users_file.write_text(
        json.dumps({"admin": {"username": "admin", "password_hash": legacy,
                              "role": "admin", "created_at": "x"}}),
        encoding="utf-8",
    )


def test_legacy_login_upgrades_to_pbkdf2_and_forces_change(store):
    _seed_legacy_admin(store)
    assert auth.authenticate("admin", "wrong") is False
    assert auth.authenticate("admin", "change-me") is True
    rec = json.loads(store.read_text())["admin"]
    assert rec["algo"] == "pbkdf2_sha256"
    assert rec.get("salt")
    assert rec["must_change_password"] is True


def test_password_policy(store):
    auth.init_users()
    assert auth.create_user("bob", "short")[0] is False          # too short
    assert auth.create_user("bob", "password")[0] is False       # no digit
    assert auth.create_user("user1234", "user1234")[0] is False  # equals username
    assert auth.create_user("bob", "Strong1pass")[0] is True
    assert auth.create_user("bob", "Strong1pass")[0] is False    # duplicate


def test_email_validation(store):
    auth.init_users()
    assert auth.create_user("carol", "Valid1pass", "not-an-email")[0] is False
    ok, _ = auth.create_user("carol", "Valid1pass", "carol@example.com")
    assert ok
    assert auth.get_user("carol")["email"] == "carol@example.com"


def test_change_password_rotates_hash(store):
    auth.init_users()
    auth.create_user("bob", "Strong1pass")
    assert auth.change_password("bob", "wrong", "New1pass2")[0] is False
    assert auth.change_password("bob", "Strong1pass", "Strong1pass")[0] is False
    assert auth.change_password("bob", "Strong1pass", "New1pass2")[0] is True
    assert auth.authenticate("bob", "New1pass2") is True
    assert auth.authenticate("bob", "Strong1pass") is False


def test_no_plaintext_passwords_on_disk(store):
    auth.init_users()
    auth.create_user("bob", "Strong1pass")
    auth.change_password("bob", "Strong1pass", "New1pass2")
    blob = store.read_text()
    assert "Strong1pass" not in blob
    assert "New1pass2" not in blob
