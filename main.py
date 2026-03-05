"""Agentic HR System — interactive CLI entry point."""

from __future__ import annotations

import sys

from agents.orchestrator import Orchestrator
from tools.logger import get_logger


def main() -> None:
    logger = get_logger("main")
    logger.info("Starting Agentic HR System")

    orchestrator = Orchestrator()

    print("=" * 60)
    print("  Agentic HR System")
    print("  Type your HR request below. Type 'quit' to exit.")
    print("=" * 60)

    while True:
        try:
            user_input = input("\n[You] > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        response = orchestrator.handle(user_input)
        print(f"\n[HR Assistant] {response}")


if __name__ == "__main__":
    main()
