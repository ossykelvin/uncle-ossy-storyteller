import hashlib
import hmac
import json
import os
import re
from pathlib import Path
from core.config import LOCAL_STORAGE_PATH, env
from core.utils import now_iso

USERS_FILE = LOCAL_STORAGE_PATH / "users.json"

# Password hashing parameters (PBKDF2-HMAC-SHA256, stdlib only).
PBKDF2_ALGO = "pbkdf2_sha256"
PBKDF2_ITERATIONS = 200_000
SALT_BYTES = 16

# Legacy scheme kept only so old accounts can still log in once and be upgraded.
_LEGACY_STATIC_SALT = "local-mvp"
DEFAULT_ADMIN_PASSWORD = "change-me"

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


# ── Hashing ────────────────────────────────────────────────────────────

def _pbkdf2(password: str, salt: str, iterations: int = PBKDF2_ITERATIONS) -> str:
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), iterations)
    return dk.hex()


def _new_password_fields(password: str) -> dict:
    salt = os.urandom(SALT_BYTES).hex()
    return {
        "algo": PBKDF2_ALGO,
        "iterations": PBKDF2_ITERATIONS,
        "salt": salt,
        "password_hash": _pbkdf2(password, salt, PBKDF2_ITERATIONS),
    }


def _legacy_hash(password: str) -> str:
    return hashlib.sha256(f"{_LEGACY_STATIC_SALT}:{password}".encode("utf-8")).hexdigest()


def _verify_password(user: dict, password: str) -> tuple[bool, bool]:
    """Return (is_valid, needs_upgrade).

    needs_upgrade is True when the stored record used the old static-salt scheme,
    so the caller can rehash with PBKDF2 after a successful login.
    """
    stored = user.get("password_hash", "")
    if not stored:
        return False, False
    if user.get("algo") == PBKDF2_ALGO and user.get("salt"):
        candidate = _pbkdf2(password, user["salt"], int(user.get("iterations", PBKDF2_ITERATIONS)))
        return hmac.compare_digest(stored, candidate), False
    # Legacy static-salt SHA-256 record.
    return hmac.compare_digest(stored, _legacy_hash(password)), True


# ── Password policy ────────────────────────────────────────────────────

def validate_password(password: str, username: str = "") -> tuple[bool, str]:
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if username and password.strip().lower() == username.strip().lower():
        return False, "Password must not be the same as the username."
    if password == DEFAULT_ADMIN_PASSWORD:
        return False, "Choose a password other than the default."
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        return False, "Password must include at least one letter and one number."
    return True, "OK"


# ── User store ─────────────────────────────────────────────────────────

def init_users() -> None:
    LOCAL_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
    if USERS_FILE.exists():
        return
    admin_username = env("LOCAL_ADMIN_USERNAME", "admin")
    admin_password = env("LOCAL_ADMIN_PASSWORD", DEFAULT_ADMIN_PASSWORD)
    record = {
        "username": admin_username,
        "email": env("LOCAL_ADMIN_EMAIL", ""),
        "role": "admin",
        # Force a password change on first login if the default is still in place.
        "must_change_password": admin_password == DEFAULT_ADMIN_PASSWORD,
        "created_at": now_iso(),
    }
    record.update(_new_password_fields(admin_password))
    _write_users({admin_username: record})


def _write_users(users: dict) -> None:
    USERS_FILE.write_text(json.dumps(users, indent=2), encoding="utf-8")


def load_users() -> dict:
    init_users()
    return json.loads(USERS_FILE.read_text(encoding="utf-8"))


def get_user(username: str) -> dict | None:
    return load_users().get(username)


def authenticate(username: str, password: str) -> bool:
    users = load_users()
    user = users.get(username)
    if not user:
        return False
    ok, needs_upgrade = _verify_password(user, password)
    if ok and needs_upgrade:
        # Transparently migrate the legacy hash to PBKDF2 on successful login.
        user.update(_new_password_fields(password))
        if "must_change_password" not in user:
            # An upgraded account still on the default password must rotate it.
            user["must_change_password"] = password == DEFAULT_ADMIN_PASSWORD
        users[username] = user
        _write_users(users)
    return ok


def must_change_password(username: str) -> bool:
    user = get_user(username)
    return bool(user and user.get("must_change_password"))


def create_user(username: str, password: str, email: str = "") -> tuple[bool, str]:
    username = username.strip()
    email = (email or "").strip()
    if not username or not password:
        return False, "Username and password are required."
    if email and not EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    ok, msg = validate_password(password, username)
    if not ok:
        return False, msg
    users = load_users()
    if username in users:
        return False, "User already exists."
    record = {
        "username": username,
        "email": email,
        "role": "writer",
        "must_change_password": False,
        "created_at": now_iso(),
    }
    record.update(_new_password_fields(password))
    users[username] = record
    _write_users(users)
    return True, "User created."


def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    users = load_users()
    user = users.get(username)
    if not user:
        return False, "User not found."
    ok, _ = _verify_password(user, old_password)
    if not ok:
        return False, "Current password is incorrect."
    valid, msg = validate_password(new_password, username)
    if not valid:
        return False, msg
    if new_password == old_password:
        return False, "New password must be different from the current one."
    user.update(_new_password_fields(new_password))
    user["must_change_password"] = False
    users[username] = user
    _write_users(users)
    return True, "Password updated."
