"""Tools for recruitment data."""

from __future__ import annotations

import json
from config.settings import settings


def _load_positions() -> list[dict]:
    path = settings.data_dir / "open_positions.json"
    with open(path) as f:
        return json.load(f)


def get_open_positions(status: str = "open") -> list[dict]:
    """Get positions filtered by status (open/closed/all)."""
    positions = _load_positions()
    if status == "all":
        return positions
    return [p for p in positions if p["status"] == status]
