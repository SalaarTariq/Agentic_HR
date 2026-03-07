"""Chat session management — stores conversations in separate JSON files."""

from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

from config.settings import settings

_SESSIONS_DIR = settings.memory_dir / "sessions"
_ID_PATTERN = re.compile(r"^[a-f0-9]{12}$")


def _ensure_dir() -> None:
    _SESSIONS_DIR.mkdir(parents=True, exist_ok=True)


def _validate_id(session_id: str) -> None:
    if not _ID_PATTERN.match(session_id):
        raise ValueError(f"Invalid session id: {session_id}")


def _session_path(session_id: str) -> Path:
    _validate_id(session_id)
    return _SESSIONS_DIR / f"{session_id}.json"


def _read_session(path: Path) -> dict:
    return json.loads(path.read_text())


def _write_session(path: Path, session: dict) -> None:
    path.write_text(json.dumps(session, indent=2))


def create_session(title: str = "") -> dict:
    """Create a new chat session and return it."""
    _ensure_dir()
    now = datetime.now(timezone.utc).isoformat()
    session = {
        "id": uuid.uuid4().hex[:12],
        "title": title or "New Chat",
        "created_at": now,
        "updated_at": now,
        "messages": [],
    }
    _write_session(_session_path(session["id"]), session)
    return session


def get_session(session_id: str) -> dict | None:
    """Return a session by id, or None if not found."""
    try:
        path = _session_path(session_id)
    except ValueError:
        return None
    if not path.exists():
        return None
    return _read_session(path)


def list_sessions() -> list[dict]:
    """Return all sessions (without messages), sorted by most recent."""
    _ensure_dir()
    sessions = []
    for p in _SESSIONS_DIR.glob("*.json"):
        try:
            data = json.loads(p.read_text())
            sessions.append({
                "id": data["id"],
                "title": data["title"],
                "created_at": data["created_at"],
                "updated_at": data["updated_at"],
                "message_count": len(data.get("messages", [])),
            })
        except (json.JSONDecodeError, KeyError):
            continue
    sessions.sort(key=lambda s: s["updated_at"], reverse=True)
    return sessions


def add_message_to_session(
    session_id: str, role: str, content: str, metadata: dict | None = None
) -> dict | None:
    """Append a message to the session. Returns updated session or None."""
    session = get_session(session_id)
    if session is None:
        return None
    now = datetime.now(timezone.utc).isoformat()
    entry = {"timestamp": now, "role": role, "content": content}
    if metadata:
        entry["metadata"] = metadata
    session["messages"].append(entry)
    session["updated_at"] = now
    # Auto-title from first user message
    if role == "user" and session["title"] == "New Chat":
        session["title"] = content[:50].strip()
    _write_session(_session_path(session_id), session)
    return session


def delete_session(session_id: str) -> bool:
    """Delete a session file. Returns True if deleted."""
    try:
        path = _session_path(session_id)
    except ValueError:
        return False
    if path.exists():
        path.unlink()
        return True
    return False


def update_session_title(session_id: str, title: str) -> dict | None:
    """Rename a session. Returns updated session or None."""
    session = get_session(session_id)
    if session is None:
        return None
    session["title"] = title
    session["updated_at"] = datetime.now(timezone.utc).isoformat()
    _write_session(_session_path(session_id), session)
    return session


def get_recent_session_messages(session_id: str, n: int = 5) -> list[dict]:
    """Return the last n messages from a session."""
    session = get_session(session_id)
    if session is None:
        return []
    return session["messages"][-n:]
