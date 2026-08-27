# logic-analyzer-mcp — AGENTS.md

FastMCP 3.2+ server for USB logic analyzers (sigrok + simulator). Six portmanteau tools; Vite React webapp; Tauri native wrapper.

## Quick-ref

- Install: `uv sync --extra dev`
- Serve (stdio): `just serve` | HTTP: `just serve-http` (port 10985)
- Webapp: `just webapp` → http://127.0.0.1:10989
- Lint/type: `just lint` | Tests: `just test` | MCPB: `just mcpb-pack`

## Ports

| Port | Service |
|------|---------|
| 10985 | Backend (FastAPI + MCP `/mcp`) |
| 10989 | Frontend (Vite React) | [Changed 2026-08-27: was 10988, collided with vienna-life-assistant]

## Tool patterns

All tools are portmanteaus with an `operation` enum: `la_device`, `la_configure`, `la_trigger`, `la_capture`, `la_decode`, `la_help`. Return `{"success": bool, "message": str, "data": ...}`.

## Key files

| File | Purpose |
|------|---------|
| `src/logic_analyzer_mcp/app.py` | FastMCP instance + tool registration |
| `src/logic_analyzer_mcp/server.py` | Entry point (`main()`), transport selection |
| `src/logic_analyzer_mcp/transport.py` | stdio/http/sse unified transport config |
| `src/logic_analyzer_mcp/config.py` | Pydantic settings (`LOGIC_ANALYZER_MCP_*`) |
| `src/logic_analyzer_mcp/web.py` | FastAPI webapp backend (REST + `/mcp` mount) |
| `src/logic_analyzer_mcp/activity_log.py` | Activity logging (opt-in) |
| `webapp/src/pages/` | React pages (device, configure, trigger, trace, decode, logs, ...) |
| `native/` | Tauri 2.0 NSIS wrapper (embedded PyInstaller backend) |

## Env

See `.env.example`. Key: `LOGIC_ANALYZER_MCP_BACKEND=auto|simulator|sigrok`.
