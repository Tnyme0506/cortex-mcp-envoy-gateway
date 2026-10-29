# Cortex MCP Envoy Gateway

Personal demo project by **Suchandra Siripuram** (`Tnyme0506`).

An AI agent gateway that combines:

- **Cortex-style Agent API** (FastAPI) — search + grounded agent query
- **MCP (Model Context Protocol)** — tools that call the Cortex API
- **Envoy** — edge proxy for routing, timeouts, and a single public port

```text
LLM / MCP Client ──► Envoy :8088 ──► FastAPI Cortex API :8080
                         ▲
                   MCP tools (stdio)
```

> Mock mode works with **no cloud credentials**. You can later point `CORTEX_MODE=snowflake` at a real Cortex Agent endpoint.

## Quick start (Docker)

```bash
docker compose up --build
```

- API via Envoy: http://localhost:8088/docs  
- Direct API: http://localhost:8080/docs  
- Envoy admin: http://localhost:9901  

Smoke test:

```bash
python scripts/smoke_test.py
```

Example call through Envoy:

```bash
curl -s http://localhost:8088/v1/cortex/agent/query ^
  -H "Content-Type: application/json" ^
  -d "{\"question\":\"How do Envoy and MCP work together?\"}"
```

## MCP client config (Cursor / Claude Desktop)

1. Keep the stack running (`docker compose up`).
2. Copy `mcp.config.example.json` into your MCP settings.
3. Tools exposed:
   - `cortex_search`
   - `cortex_agent_query`
   - `gateway_health`

Local stdio server (from repo root, with venv installed):

```bash
pip install -r requirements.txt
set PYTHONPATH=.
set CORTEX_API_BASE=http://127.0.0.1:8088
python -m mcp_server
```

## Local API only (no Docker)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set PYTHONPATH=.
uvicorn api.main:app --reload --port 8080
```

## Project layout

| Path | Role |
| --- | --- |
| `api/` | Cortex-style FastAPI service |
| `mcp_server/` | MCP tools wrapping the API |
| `envoy/envoy.yaml` | Envoy listener + routes |
| `docker-compose.yml` | API + Envoy stack |
| `scripts/smoke_test.py` | End-to-end check via gateway |

## Publish to GitHub

```bash
cd cortex-mcp-envoy-gateway
git init
git add .
git commit -m "Add Cortex API + MCP + Envoy gateway demo"
gh repo create cortex-mcp-envoy-gateway --public --source=. --remote=origin --push
```

Repo URL to put on the resume: `https://github.com/Tnyme0506/cortex-mcp-envoy-gateway`

## Interview talking points

1. **Cortex API** — agent/search contract, mock vs real backend swap via env.
2. **MCP** — tools as the LLM-facing interface over HTTP APIs.
3. **Envoy** — single ingress, path routing, timeouts, admin stats.
