"""Cortex-style Agent API (FastAPI).

Exposes search + agent-query endpoints that MCP tools and Envoy can front.
"""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from api.cortex_client import SETTINGS, cortex_agent_query, cortex_search

app = FastAPI(
    title="Cortex-style Agent API",
    description="Demo API for Cortex search/agent patterns, MCP tooling, and Envoy routing.",
    version="1.0.0",
)


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1)
    top_k: int = Field(default=3, ge=1, le=10)


class AgentRequest(BaseModel):
    question: str = Field(..., min_length=1)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "cortex_mode": SETTINGS.cortex_mode}


@app.post("/v1/cortex/search")
async def search(body: SearchRequest) -> dict:
    try:
        hits = await cortex_search(body.query, top_k=body.top_k)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"query": body.query, "results": hits}


@app.post("/v1/cortex/agent/query")
async def agent_query(body: AgentRequest) -> dict:
    try:
        result = await cortex_agent_query(body.question)
    except RuntimeError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {
        "question": body.question,
        "answer": result.answer,
        "sources": result.sources,
        "mode": result.mode,
    }
