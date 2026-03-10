"""Conversation memory — persists context across interactions."""

from __future__ import annotations

import json
import threading
from datetime import datetime, timezone

from config.settings import settings

_lock = threading.Lock()

_MEMORY_FILE = settings.memory_dir / "conversation_log.json"


def _ensure_file() -> None:
    if not _MEMORY_FILE.exists():
        _MEMORY_FILE.parent.mkdir(parents=True, exist_ok=True)
        _MEMORY_FILE.write_text("[]")


def save_memory(role: str, content: str, metadata: dict | None = None) -> None:
    """Append a message to the conversation log."""
    _ensure_file()
    with _lock:
        log: list[dict] = json.loads(_MEMORY_FILE.read_text())
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "role": role,
            "content": content,
        }
        if metadata:
            entry["metadata"] = metadata
        log.append(entry)
        _MEMORY_FILE.write_text(json.dumps(log, indent=2))


def get_recent_memory(n: int = 10) -> list[dict]:
    """Return the last *n* conversation entries."""
    _ensure_file()
    log: list[dict] = json.loads(_MEMORY_FILE.read_text())
    return log[-n:]
