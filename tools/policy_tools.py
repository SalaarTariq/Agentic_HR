"""Tools for searching and retrieving HR policy documents."""

from __future__ import annotations

import json
from config.settings import settings


def _load_policies() -> list[dict]:
    path = settings.data_dir / "policies.json"
    with open(path) as f:
        return json.load(f)


STOP_WORDS = {"what", "is", "the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "my", "our", "how", "do", "does", "can", "i", "we", "about", "me", "tell", "please"}


def search_policies(query: str) -> list[dict]:
    """Search policies by keyword. Returns matching policy objects."""
    policies = _load_policies()
    keywords = [w for w in query.lower().split() if w not in STOP_WORDS and len(w) > 2]

    def _score(policy: dict) -> int:
        text = (policy["title"] + " " + policy["content"]).lower()
        return sum(1 for kw in keywords if kw in text)

    scored = [(p, _score(p)) for p in policies]
    results = [p for p, s in scored if s > 0]
    results.sort(key=lambda p: next(s for pp, s in scored if pp is p), reverse=True)
    return results if results else [{"message": f"No policies found matching '{query}'."}]
