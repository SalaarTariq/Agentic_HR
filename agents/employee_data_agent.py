"""Employee Data Agent — looks up and summarises employee records."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from tools.employee_tools import lookup_employee, list_employees
from tools.session_tools import get_recent_session_messages


class EmployeeDataAgent(BaseAgent):
    name = "employee_data"
    prompt_file = "employee_data_agent.txt"

    def handle(self, user_message: str, session_id: str | None = None) -> str:
        history = get_recent_session_messages(session_id, 10) if session_id else None
        # Try direct lookup first; if nothing useful, list all
        result = lookup_employee(user_message)
        if isinstance(result, dict) and "message" in result:
            result = list_employees()
        return self.run(user_message, context_data=result, history=history)
