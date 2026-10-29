"""Cortex-style agent client.

Runs in mock mode by default so the demo works without cloud credentials.
Swap CORTEX_MODE=snowflake and set credentials to call a real Cortex Agent API.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    cortex_mode: str = "mock"
    snowflake_account_url: str | None = None
    snowflake_user: str | None = None
    snowflake_password: str | None = None
    cortex_agent_name: str | None = None


SETTINGS = Settings()

# Small in-memory corpus so search/agent demos are deterministic and interview-friendly.
KNOWLEDGE_BASE: list[dict[str, str]] = [
    {
        "id": "doc-envoy-mcp",
        "title": "Envoy as an MCP gateway",
        "text": (
            "Envoy can front Model Context Protocol traffic to add TLS termination, "
            "routing, retries, and observability for agent tool calls."
        ),
        "tags": "envoy mcp gateway proxy",
    },
    {
        "id": "doc-cortex-agents",
        "title": "Cortex-style agent APIs",
        "text": (
            "A Cortex-style agent API accepts natural-language questions, retrieves "
            "relevant context, and returns grounded answers with source citations."
        ),
        "tags": "cortex api agent rag",
    },
    {
        "id": "doc-mcp-tools",
        "title": "MCP tool exposure",
        "text": (
            "MCP servers expose tools, resources, and prompts so LLM clients can call "
            "backend APIs through a standard protocol instead of custom integrations."
        ),
        "tags": "mcp tools agents fastapi",
    },
]


@dataclass
class CortexAnswer:
    answer: str
    sources: list[dict[str, Any]]
    mode: str


def _score(query: str, doc: dict[str, str]) -> int:
    tokens = {t.lower() for t in query.replace("-", " ").split() if len(t) > 2}
    hay = f"{doc['title']} {doc['text']} {doc['tags']}".lower()
    return sum(1 for t in tokens if t in hay)


def mock_search(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    ranked = sorted(KNOWLEDGE_BASE, key=lambda d: _score(query, d), reverse=True)
    hits = []
    for doc in ranked[:top_k]:
        score = _score(query, doc)
        if score == 0 and hits:
            break
        hits.append(
            {
                "id": doc["id"],
                "title": doc["title"],
                "snippet": doc["text"],
                "score": score,
            }
        )
    return hits or [
        {
            "id": ranked[0]["id"],
            "title": ranked[0]["title"],
            "snippet": ranked[0]["text"],
            "score": 0,
        }
    ]


def mock_agent_query(question: str) -> CortexAnswer:
    sources = mock_search(question, top_k=2)
    joined = " ".join(s["snippet"] for s in sources)
    answer = (
        f"Based on retrieved Cortex context: {joined} "
        f"(Responding to: {question.strip()})"
    )
    return CortexAnswer(answer=answer, sources=sources, mode="mock")


async def cortex_search(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    if SETTINGS.cortex_mode.lower() == "snowflake":
        # Placeholder for a real Cortex Search / Agent HTTP call.
        # Keep mock behavior until credentials and endpoint are configured.
        if not SETTINGS.snowflake_account_url:
            raise RuntimeError(
                "CORTEX_MODE=snowflake requires SNOWFLAKE_ACCOUNT_URL and credentials"
            )
    return mock_search(query, top_k=top_k)


async def cortex_agent_query(question: str) -> CortexAnswer:
    if SETTINGS.cortex_mode.lower() == "snowflake":
        if not SETTINGS.snowflake_account_url:
            raise RuntimeError(
                "CORTEX_MODE=snowflake requires SNOWFLAKE_ACCOUNT_URL and credentials"
            )
    return mock_agent_query(question)
