"""HR Orchestrator — the central brain that classifies and routes requests."""

from __future__ import annotations

import json

from agents.base_agent import BaseAgent
from agents.policy_agent import PolicyAgent
from agents.employee_data_agent import EmployeeDataAgent
from agents.recruitment_agent import RecruitmentAgent
from agents.grievance_agent import GrievanceAgent
from tools.llm_client import chat
from tools.memory_tools import save_memory, get_recent_memory
from tools.logger import get_logger
from config.settings import settings


class Orchestrator:
    """Listen → Understand → Decide → Act → Remember."""

    def __init__(self) -> None:
        self.logger = get_logger("orchestrator")
        self._system_prompt = self._load_prompt()
        self._agents = {
            "policy": PolicyAgent(),
            "employee_data": EmployeeDataAgent(),
            "recruitment": RecruitmentAgent(),
            "grievance": GrievanceAgent(),
        }

    def _load_prompt(self) -> str:
        path = settings.prompts_dir / "orchestrator.txt"
        return path.read_text().strip() if path.exists() else ""

    # ── classification ──────────────────────────────────────────────

    def _classify(self, user_message: str) -> dict:
        """Use the LLM to classify the user's intent."""
        recent = get_recent_memory(5)
        history_text = ""
        if recent:
            history_text = "Recent conversation:\n" + "\n".join(
                f"- [{m['role']}]: {m['content'][:100]}" for m in recent
            )

        augmented = user_message
        if history_text:
            augmented = f"{history_text}\n\nNew message: {user_message}"

        raw = chat(self._system_prompt, augmented, temperature=0.0)
        self.logger.debug("Classification raw: %s", raw)

        try:
            # Strip markdown fences if the LLM wraps in ```json ... ```
            cleaned = raw.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned)
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse classification, treating as out_of_scope.")
            return {
                "intent": "out_of_scope",
                "confidence": 0.0,
                "summary": user_message,
                "clarification_question": None,
            }

    # ── routing ─────────────────────────────────────────────────────

    def handle(self, user_message: str) -> str:
        """Main entry: classify, route, remember."""
        self.logger.info("Received: %s", user_message[:120])
        save_memory("user", user_message)

        classification = self._classify(user_message)
        intent = classification.get("intent", "out_of_scope")
        confidence = classification.get("confidence", 0.0)
        self.logger.info("Intent: %s (%.2f)", intent, confidence)

        # Handle non-routable intents
        if intent == "clarification":
            question = classification.get("clarification_question", "Could you please clarify your request?")
            save_memory("assistant", question, {"intent": "clarification"})
            return question

        if intent == "out_of_scope":
            msg = "I'm sorry, I can only help with HR-related requests such as policies, employee information, recruitment, or grievances."
            save_memory("assistant", msg, {"intent": "out_of_scope"})
            return msg

        # Route to specialist
        agent = self._agents.get(intent)
        if agent is None:
            msg = f"I identified your request as '{intent}' but don't have a specialist for that yet."
            save_memory("assistant", msg, {"intent": intent})
            return msg

        self.logger.info("Routing to %s agent", intent)
        response = agent.handle(user_message)
        save_memory("assistant", response, {"intent": intent, "confidence": confidence})
        return response
