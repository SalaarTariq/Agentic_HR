"""Tools for looking up employee data."""

from __future__ import annotations

import json
from config.settings import settings


def _load_employees() -> list[dict]:
    path = settings.data_dir / "employees.json"
    with open(path) as f:
        return json.load(f)


def lookup_employee(query: str) -> dict | list[dict]:
    """Look up an employee by name, ID, or email (partial match)."""
    employees = _load_employees()
    query_lower = query.lower()
    results = [
        e for e in employees
        if query_lower in e["name"].lower()
        or query_lower in e["id"].lower()
        or query_lower in e["email"].lower()
    ]
    if len(results) == 1:
        return results[0]
    if results:
        return results
    return {"message": f"No employee found matching '{query}'."}


def list_employees(department: str | None = None) -> list[dict]:
    """List all employees, optionally filtered by department."""
    employees = _load_employees()
    if department:
        employees = [e for e in employees if e["department"].lower() == department.lower()]
    return employees
