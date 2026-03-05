"""Recruitment Agent — manages open positions and candidate pipelines."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from tools.recruitment_tools import get_open_positions


class RecruitmentAgent(BaseAgent):
    name = "recruitment"
    prompt_file = "recruitment_agent.txt"

    def handle(self, user_message: str) -> str:
        positions = get_open_positions(status="open")
        return self.run(user_message, context_data=positions)
