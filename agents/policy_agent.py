"""Policy Agent — answers questions about company HR policies."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from tools.policy_tools import search_policies


class PolicyAgent(BaseAgent):
    name = "policy"
    prompt_file = "policy_agent.txt"

    def handle(self, user_message: str) -> str:
        policies = search_policies(user_message)
        return self.run(user_message, context_data=policies)
