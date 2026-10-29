"""Quick smoke test against the Envoy gateway (preferred) or direct API."""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

BASE = os.getenv("GATEWAY_PUBLIC_URL", "http://127.0.0.1:8088").rstrip("/")


def post(path: str, payload: dict) -> dict:
    req = urllib.request.Request(
        f"{BASE}{path}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main() -> int:
    try:
        with urllib.request.urlopen(f"{BASE}/health", timeout=10) as resp:
            health = json.loads(resp.read().decode())
        print("health:", health)

        search = post("/v1/cortex/search", {"query": "Envoy MCP gateway", "top_k": 2})
        print("search hits:", len(search.get("results", [])))

        agent = post(
            "/v1/cortex/agent/query",
            {"question": "How do Envoy and MCP work together?"},
        )
        print("agent mode:", agent.get("mode"))
        print("answer preview:", agent.get("answer", "")[:160], "...")
    except urllib.error.URLError as exc:
        print(f"Smoke test failed talking to {BASE}: {exc}", file=sys.stderr)
        print("Start the stack with: docker compose up --build", file=sys.stderr)
        return 1

    print("Smoke test passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
