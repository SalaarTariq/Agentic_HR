"""Agentic HR System — FastAPI web server."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from agents.orchestrator import Orchestrator
from tools.memory_tools import get_recent_memory
from tools.session_tools import (
    add_message_to_session,
    create_session,
    delete_session,
    get_session,
    list_sessions,
    update_session_title,
)

app = FastAPI(title="Agentic HR System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

orchestrator = Orchestrator()

STATIC_DIR = Path(__file__).resolve().parent / "static"


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    intent: str = ""
    agent: str = ""


class RenameRequest(BaseModel):
    title: str


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    # Create or use existing session
    session_id = req.session_id
    if not session_id:
        session = create_session()
        session_id = session["id"]
    elif get_session(session_id) is None:
        raise HTTPException(status_code=404, detail="Session not found")

    # Process through orchestrator — it will read session history for context
    # Do NOT save user message to session before this, to avoid the LLM
    # seeing the current message twice (once in history, once as new message).
    result = orchestrator.handle(req.message, session_id=session_id)

    # Now save both messages to the session
    add_message_to_session(session_id, "user", req.message)
    add_message_to_session(session_id, "assistant", result["response"])

    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        intent=result.get("intent", ""),
        agent=result.get("agent", ""),
    )


@app.get("/api/history")
async def history():
    return get_recent_memory(50)


# ── Session endpoints ────────────────────────────────────────────

@app.post("/api/sessions")
async def create_new_session():
    return create_session()


@app.get("/api/sessions")
async def get_all_sessions():
    return list_sessions()


@app.get("/api/sessions/{session_id}")
async def get_session_by_id(session_id: str):
    session = get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@app.delete("/api/sessions/{session_id}")
async def delete_session_by_id(session_id: str):
    if not delete_session(session_id):
        raise HTTPException(status_code=404, detail="Session not found")
    return {"ok": True}


@app.patch("/api/sessions/{session_id}")
async def rename_session(session_id: str, req: RenameRequest):
    session = update_session_title(session_id, req.title)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
