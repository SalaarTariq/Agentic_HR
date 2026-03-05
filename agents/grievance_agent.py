"""Grievance Agent — files and tracks employee grievances."""

from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from tools.grievance_tools import file_grievance
from tools.llm_client import chat


class GrievanceAgent(BaseAgent):
    name = "grievance"
    prompt_file = "grievance_agent.txt"

    def handle(self, user_message: str) -> str:
        # Ask the LLM to extract structured grievance info
        extraction_prompt = (
            "Extract the following from the user message as JSON: "
            '{"employee_id": "...", "category": "...", "description": "..."}. '
            "If information is missing, use reasonable defaults. "
            'Valid categories: general, harassment, safety, discrimination, workplace, other.'
        )
        raw = chat(extraction_prompt, user_message)

        try:
            data = json.loads(raw)
            record = file_grievance(
                employee_id=data.get("employee_id", "unknown"),
                category=data.get("category", "general"),
                description=data.get("description", user_message),
            )
            return self.run(
                user_message,
                context_data={
                    "grievance_filed": record,
                    "message": "Grievance has been recorded successfully.",
                },
            )
        except (json.JSONDecodeError, KeyError):
            # Fallback: file with raw description
            record = file_grievance(
                employee_id="unknown",
                category="general",
                description=user_message,
            )
            return self.run(
                user_message,
                context_data={
                    "grievance_filed": record,
                    "message": "Grievance recorded (some details may need follow-up).",
                },
            )
