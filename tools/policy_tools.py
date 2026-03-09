"""Tools for searching and retrieving HR policy documents."""

from __future__ import annotations

import json
from config.settings import settings


def _load_policies() -> list[dict]:
    path = settings.data_dir / "policies.json"
    with open(path) as f:
        return json.load(f)


STOP_WORDS = {"what", "is", "the", "a", "an", "of", "for", "to", "in", "on", "and", "or", "my", "our", "how", "do", "does", "can", "i", "we", "about", "me", "tell", "please"}

# Synonym map: common terms → canonical keywords found in policy docs
SYNONYMS: dict[str, list[str]] = {
    "vacation": ["leave", "time off", "pto"],
    "pto": ["leave", "time off", "vacation"],
    "time off": ["leave", "vacation", "pto"],
    "wfh": ["remote work", "work from home", "telecommute"],
    "work from home": ["remote work", "wfh", "telecommute"],
    "telecommute": ["remote work", "wfh", "work from home"],
    "sick": ["leave", "medical", "health"],
    "salary": ["compensation", "pay", "wages"],
    "pay": ["compensation", "salary", "wages"],
    "wages": ["compensation", "salary", "pay"],
    "fired": ["termination", "dismissal"],
    "termination": ["fired", "dismissal"],
    "holiday": ["leave", "time off", "vacation"],
    "dress": ["dress code", "attire", "clothing"],
    "attire": ["dress code", "dress", "clothing"],
    "conduct": ["code of conduct", "behavior", "ethics"],
    "ethics": ["code of conduct", "conduct", "behavior"],
    "insurance": ["benefits", "health", "medical"],
    "benefits": ["insurance", "health", "compensation"],
    "maternity": ["parental leave", "maternity leave"],
    "paternity": ["parental leave", "paternity leave"],
}


def _expand_keywords(keywords: list[str]) -> list[str]:
    """Expand keywords with synonyms for fuzzy matching."""
    expanded = list(keywords)
    for kw in keywords:
        if kw in SYNONYMS:
            expanded.extend(SYNONYMS[kw])
    return list(set(expanded))


def search_policies(query: str) -> list[dict]:
    """Search policies by keyword with synonym expansion. Returns matching policy objects."""
    policies = _load_policies()
    keywords = [w for w in query.lower().split() if w not in STOP_WORDS and len(w) > 2]
    expanded = _expand_keywords(keywords)

    def _score(policy: dict) -> int:
        text = (policy["title"] + " " + policy["content"]).lower()
        return sum(1 for kw in expanded if kw in text)

    scored = [(p, _score(p)) for p in policies]
    results = [p for p, s in scored if s > 0]
    results.sort(key=lambda p: next(s for pp, s in scored if pp is p), reverse=True)
    return results if results else [{"message": f"No policies found matching '{query}'."}]
