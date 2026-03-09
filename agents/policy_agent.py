"""Policy Agent — answers questions about company HR policies."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from tools.policy_tools import search_policies
from tools.session_tools import get_recent_session_messages


class PolicyAgent(BaseAgent):
    name = "policy"
    prompt_file = "policy_agent.txt"

    def handle(self, user_message: str, session_id: str | None = None) -> str:
        history = get_recent_session_messages(session_id, 10) if session_id else None
        policies = search_policies(user_message)
        return self.run(user_message, context_data=policies, history=history)
