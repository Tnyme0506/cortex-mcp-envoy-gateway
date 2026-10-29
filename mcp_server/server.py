"""MCP server that wraps the Cortex-style Agent API.

Tools:
  - cortex_search: semantic/keyword retrieval over Cortex context
  - cortex_agent_query: grounded agent answer with citations
"""

from __future__ import annotations

import json
import os

import httpx
from mcp.server.fastmcp import FastMCP

CORTEX_API_BASE = os.getenv("CORTEX_API_BASE", "http://127.0.0.1:8080").rstrip("/")

mcp = FastMCP(
    "cortex-mcp-envoy-gateway",
    instructions=(
        "Tools for querying a Cortex-style agent API. Prefer cortex_search for "
        "retrieval and cortex_agent_query for grounded answers."
    ),
)


async def _post(path: str, payload: dict) -> dict:
    url = f"{CORTEX_API_BASE}{path}"
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(url, json=payload)
        response.raise_for_status()
        return response.json()


@mcp.tool()
async def cortex_search(query: str, top_k: int = 3) -> str:
    """Search Cortex-style knowledge context and return ranked snippets."""
    data = await _post("/v1/cortex/search", {"query": query, "top_k": top_k})
    return json.dumps(data, indent=2)


@mcp.tool()
async def cortex_agent_query(question: str) -> str:
    """Ask a Cortex-style agent a question and return an answer with sources."""
    data = await _post("/v1/cortex/agent/query", {"question": question})
    return json.dumps(data, indent=2)


@mcp.tool()
async def gateway_health() -> str:
    """Check whether the Cortex API behind the gateway is healthy."""
    url = f"{CORTEX_API_BASE}/health"
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(url)
        response.raise_for_status()
        return json.dumps(response.json(), indent=2)


if __name__ == "__main__":
    # stdio transport: works with Claude Desktop / Cursor MCP configs
    mcp.run(transport="stdio")
