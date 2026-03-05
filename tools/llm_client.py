"""Thin wrapper around the Google Gemini API (google-genai SDK)."""

from __future__ import annotations

from google import genai
from google.genai import types

from config.settings import settings

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=settings.gemini_api_key)
    return _client


def chat(
    system_prompt: str,
    user_message: str,
    history: list[dict] | None = None,
    temperature: float | None = None,
) -> str:
    """Send a chat request to Gemini and return the response text."""
    client = _get_client()

    contents = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append(types.Content(role=role, parts=[types.Part(text=msg["content"])]))
    contents.append(types.Content(role="user", parts=[types.Part(text=user_message)]))

    config = types.GenerateContentConfig(
        system_instruction=system_prompt if system_prompt else None,
        temperature=temperature if temperature is not None else settings.temperature,
    )

    response = client.models.generate_content(
        model=settings.model_name,
        contents=contents,
        config=config,
    )
    return response.text or ""
