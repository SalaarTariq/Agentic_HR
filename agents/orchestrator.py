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
from tools.session_tools import get_recent_session_messages
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

    def _classify(self, user_message: str, session_id: str | None = None) -> dict:
        """Use the LLM to classify the user's intent."""
        if session_id:
            recent = get_recent_session_messages(session_id, 5)
        else:
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

    # ── general chat ─────────────────────────────────────────────────

    _GENERAL_CHAT_PROMPT = (
        "You are a friendly, warm HR assistant chatbot. "
        "Respond naturally to the user's message — greetings, small talk, "
        "emotional expressions, thank-yous, or general questions about what you can do. "
        "Be empathetic and supportive. If the user seems stressed or upset, "
        "acknowledge their feelings and gently remind them you're here to help with HR needs. "
        "Keep responses concise (2-3 sentences). "
        "You can help with: company policies, employee information, recruitment, and grievances."
    )

    def _handle_general_chat(self, user_message: str, session_id: str | None = None) -> str:
        """Handle greetings, small talk, and general conversational messages."""
        if session_id:
            recent = get_recent_session_messages(session_id, 5)
        else:
            recent = get_recent_memory(5)

        history = []
        if recent:
            history = [{"role": m["role"], "content": m["content"]} for m in recent]

        return chat(self._GENERAL_CHAT_PROMPT, user_message, history=history)

    # ── routing ─────────────────────────────────────────────────────

    def handle(self, user_message: str, session_id: str | None = None) -> str:
        """Main entry: classify, route, remember."""
        self.logger.info("Received: %s", user_message[:120])
        save_memory("user", user_message)

        classification = self._classify(user_message, session_id=session_id)
        intent = classification.get("intent", "out_of_scope")
        confidence = classification.get("confidence", 0.0)
        self.logger.info("Intent: %s (%.2f)", intent, confidence)

        # Handle non-routable intents
        if intent == "clarification":
            question = classification.get("clarification_question", "Could you please clarify your request?")
            save_memory("assistant", question, {"intent": "clarification"})
            return question

        if intent == "general_chat":
            response = self._handle_general_chat(user_message, session_id)
            save_memory("assistant", response, {"intent": "general_chat"})
            return response

        if intent == "out_of_scope":
            msg = "I'm sorry, that falls outside what I can help with. I'm your HR assistant — I can help with company policies, employee information, recruitment, or grievances. How can I assist you today?"
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
