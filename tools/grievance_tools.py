"""Tools for filing and tracking grievances."""

from __future__ import annotations

import json
import threading
import uuid
from datetime import datetime, timezone

from config.settings import settings

_lock = threading.Lock()

_GRIEVANCE_FILE = settings.data_dir / "grievances.json"


def _ensure_file() -> None:
    if not _GRIEVANCE_FILE.exists():
        _GRIEVANCE_FILE.parent.mkdir(parents=True, exist_ok=True)
        _GRIEVANCE_FILE.write_text("[]")


def _load_grievances() -> list[dict]:
    _ensure_file()
    with open(_GRIEVANCE_FILE) as f:
        return json.load(f)


def _save_grievances(grievances: list[dict]) -> None:
    with open(_GRIEVANCE_FILE, "w") as f:
        json.dump(grievances, f, indent=2)


def file_grievance(employee_id: str, category: str, description: str) -> dict:
    """File a new grievance. Returns the created record."""
    valid_categories = {"general", "harassment", "safety", "discrimination", "workplace", "other"}
    category = category.lower().strip()
    if category not in valid_categories:
        category = "general"
    with _lock:
        grievances = _load_grievances()
        record = {
            "id": f"GRV-{uuid.uuid4().hex[:6].upper()}",
            "employee_id": employee_id,
            "category": category,
            "description": description,
            "status": "open",
            "filed_at": datetime.now(timezone.utc).isoformat(),
            "escalated": category in ("harassment", "safety", "discrimination"),
        }
        grievances.append(record)
        _save_grievances(grievances)
        return record
