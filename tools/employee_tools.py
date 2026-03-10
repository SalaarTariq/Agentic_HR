"""Tools for looking up employee data."""

from __future__ import annotations

import json
import re
from config.settings import settings


def _load_employees() -> list[dict]:
    path = settings.data_dir / "employees.json"
    with open(path) as f:
        return json.load(f)


# Words to strip when extracting name tokens from natural-language queries
_NOISE_WORDS = {
    "who", "what", "where", "when", "how", "is", "are", "was", "were",
    "the", "a", "an", "of", "for", "to", "in", "on", "and", "or",
    "my", "me", "tell", "about", "please", "can", "you", "do", "does",
    "find", "look", "up", "lookup", "search", "get", "show", "give",
    "manager", "department", "team", "role", "email", "phone", "info",
    "information", "details", "employee", "staff", "person", "worker",
    "his", "her", "their", "name", "called", "named",
}


def _extract_name_tokens(query: str) -> list[str]:
    """Extract likely name tokens from a natural-language query."""
    # Remove possessives and punctuation
    cleaned = re.sub(r"'s\b", "", query)
    cleaned = re.sub(r"[^\w\s]", " ", cleaned)
    tokens = [t for t in cleaned.lower().split() if t not in _NOISE_WORDS and len(t) > 1]
    return tokens


def lookup_employee(query: str) -> dict | list[dict]:
    """Look up an employee by name, ID, or email (partial match with name extraction)."""
    employees = _load_employees()

    # First try: direct match on the full query
    query_lower = query.lower()
    results = [
        e for e in employees
        if query_lower in e["name"].lower()
        or query_lower in e["id"].lower()
        or query_lower in e["email"].lower()
    ]
    if results:
        return results[0] if len(results) == 1 else results

    # Second try: extract name tokens and match individually
    tokens = _extract_name_tokens(query)
    if tokens:
        def _score(emp: dict) -> int:
            name_lower = emp["name"].lower()
            return sum(1 for t in tokens if t in name_lower)

        scored = [(e, _score(e)) for e in employees]
        ranked = sorted(
            [(e, s) for e, s in scored if s > 0],
            key=lambda pair: pair[1],
            reverse=True,
        )
        results = [e for e, _ in ranked]
        if results:
            return results[0] if len(results) == 1 else results

    return {"message": f"No employee found matching '{query}'."}


def list_employees(department: str | None = None) -> list[dict]:
    """List all employees, optionally filtered by department."""
    employees = _load_employees()
    if department:
        employees = [e for e in employees if e["department"].lower() == department.lower()]
    return employees
