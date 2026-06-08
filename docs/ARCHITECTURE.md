# Architecture

## Stack

- **FastMCP 3.2+** — MCP tool surface, resources, prompts
- **Pydantic v2** — capture/device models
- **FastAPI** — composite HTTP server (`server.py`) with `/mcp` mount and REST `/api/*`
- **uv + hatchling** — packaging; `justfile` for fleet tasks

## Layers

```
tools/portmanteau/     → la_* MCP tools
services/session.py    → backend selection + connect
services/backends/     → simulator, sigrok
services/registry.py   → last capture/decode singletons
web.py                 → REST for webapp
capabilities.py        → /api/capabilities fleet contract
```

## Transport

| Mode | Entry | Port |
|------|-------|------|
| stdio | `python -m logic_analyzer_mcp --stdio` | — |
| http | `uvicorn logic_analyzer_mcp.server:app` | 10985 |
| webapp | `webapp/start.ps1` | 10985 + 10987 |

## Data flow

1. Agent calls `la_capture(operation="single")`
2. Active backend acquires samples → `LogicCapture`
3. Registry stores last capture
4. `la_decode` reads last capture, runs sigrok decoder stack or simulator stub
5. Export utils write CSV/VCD/JSON to `LOGIC_ANALYZER_MCP_CAPTURE_DIR`
