"""Grievance Agent — files and tracks employee grievances."""

from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from tools.grievance_tools import file_grievance
from tools.llm_client import chat
from tools.session_tools import get_recent_session_messages


class GrievanceAgent(BaseAgent):
    name = "grievance"
    prompt_file = "grievance_agent.txt"

    def handle(self, user_message: str, session_id: str | None = None) -> str:
        # Ask the LLM to extract structured grievance info
        extraction_prompt = (
            "Extract the following from the user message as JSON: "
            '{"employee_id": "...", "category": "...", "description": "..."}. '
            "If information is missing, use reasonable defaults. "
            'Valid categories: general, harassment, safety, discrimination, workplace, other.'
        )
        raw = chat(extraction_prompt, user_message)

        try:
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            data = json.loads(cleaned)
            record = file_grievance(
                employee_id=data.get("employee_id", "unknown"),
                category=data.get("category", "general"),
                description=data.get("description", user_message),
            )
            history = get_recent_session_messages(session_id, 10) if session_id else None
            return self.run(
                user_message,
                context_data={
                    "grievance_filed": record,
                    "message": "Grievance has been recorded successfully.",
                },
                history=history,
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback: file with raw description
            record = file_grievance(
                employee_id="unknown",
                category="general",
                description=user_message,
            )
            history = get_recent_session_messages(session_id, 10) if session_id else None
            return self.run(
                user_message,
                context_data={
                    "grievance_filed": record,
                    "message": "Grievance recorded (some details may need follow-up).",
                },
                history=history,
            )
