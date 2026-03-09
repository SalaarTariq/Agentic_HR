"""Base class for all specialist agents."""

from __future__ import annotations

import json

from config.settings import settings
from tools.llm_client import chat
from tools.logger import get_logger


class BaseAgent:
    """Every specialist agent loads its own system prompt and uses the LLM."""

    name: str = "base"
    prompt_file: str = ""

    def __init__(self) -> None:
        self.logger = get_logger(f"agent.{self.name}")
        self._system_prompt = self._load_prompt()

    def _load_prompt(self) -> str:
        path = settings.prompts_dir / self.prompt_file
        if path.exists():
            return path.read_text().strip()
        self.logger.warning("Prompt file %s not found, using empty prompt.", path)
        return ""

    def _build_context(self, data: dict | list | str) -> str:
        """Convert tool data into a context string for the LLM."""
        if isinstance(data, str):
            return data
        return json.dumps(data, indent=2)

    def run(
        self,
        user_message: str,
        context_data: dict | list | str = "",
        history: list[dict] | None = None,
    ) -> str:
        """Run the agent: gather context, call LLM, return answer."""
        context = self._build_context(context_data)
        augmented_message = user_message
        if context:
            augmented_message = (
                f"Relevant data:\n```json\n{context}\n```\n\nUser request: {user_message}"
            )
        self.logger.info("Running with message: %s", user_message[:120])
        response = chat(self._system_prompt, augmented_message, history=history)
        self.logger.info("Response length: %d chars", len(response))
        return response
