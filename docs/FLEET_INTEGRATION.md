# Fleet Integration

## Ports

| Port | Role |
|------|------|
| 10985 | Backend HTTP + MCP `/mcp` |
| 10987 | Vite frontend |

Registered in `mcp-central-docs/operations/WEBAPP_PORTS.md`.

## Standards compliance

- Portmanteau tools (6)
- `llms.txt` + `llms-full.txt`
- `/api/capabilities` endpoint
- `justfile` + PowerShell `start.ps1`
- `glama.json` health metadata
- CI: ruff + pytest on Windows

## Pipelines

| From | To | Use case |
|------|-----|----------|
| kicad-mcp | logic-analyzer-mcp | Verify bus wiring after layout |
| oscilloscope-mcp | logic-analyzer-mcp | Mixed-signal debug |
| chip-design-mcp | logic-analyzer-mcp | FPGA bring-up on SPI/JTAG |

## mcp.json entry

See [README.md](../README.md#cursor-mcp-config).
