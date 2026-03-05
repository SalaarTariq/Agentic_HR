"""Tools for filing and tracking grievances."""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

from config.settings import settings

_GRIEVANCE_FILE = settings.data_dir / "grievances.json"


def _load_grievances() -> list[dict]:
    with open(_GRIEVANCE_FILE) as f:
        return json.load(f)


def _save_grievances(grievances: list[dict]) -> None:
    with open(_GRIEVANCE_FILE, "w") as f:
        json.dump(grievances, f, indent=2)


def file_grievance(employee_id: str, category: str, description: str) -> dict:
    """File a new grievance. Returns the created record."""
    grievances = _load_grievances()
    record = {
        "id": f"GRV-{uuid.uuid4().hex[:6].upper()}",
        "employee_id": employee_id,
        "category": category,
        "description": description,
        "status": "open",
        "filed_at": datetime.now(timezone.utc).isoformat(),
        "escalated": category.lower() in ("harassment", "safety", "discrimination"),
    }
    grievances.append(record)
    _save_grievances(grievances)
    return record
