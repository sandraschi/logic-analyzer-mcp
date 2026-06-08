# logic-analyzer-mcp - Install Guide

Naked-PC install standard for Windows. Assumes PowerShell and winget.

## Option A - Cursor MCP (recommended)

1. Clone or copy repo to `D:\Dev\repos\logic-analyzer-mcp`
2. Install [uv](https://docs.astral.sh/uv/): `winget install astral-sh.uv`
3. Sync dependencies:

```powershell
Set-Location D:\Dev\repos\logic-analyzer-mcp
uv sync --extra dev
```

4. Add MCP entry to `C:\Users\sandr\.cursor\mcp.json` (see [README.md](README.md#cursor-mcp-config))
5. Restart Cursor
6. Verify: `la_help(operation="status")`

## Option A2 - Claude Desktop MCPB

1. Build or download `logic-analyzer-mcp-v0.1.0.mcpb` from [Releases](https://github.com/sandraschi/logic-analyzer-mcp/releases)
2. Or build locally:

```powershell
Set-Location D:\Dev\repos\logic-analyzer-mcp
npx --yes @anthropic-ai/mcpb@latest validate .
npx --yes @anthropic-ai/mcpb@latest pack . dist/logic-analyzer-mcp-v0.1.0.mcpb
```

3. Drag the `.mcpb` file into Claude Desktop
4. Requires [uv](https://docs.astral.sh/uv/) on PATH; for hardware also install sigrok-cli (PulseView)

## Option B - HTTP mode (remote agents)

```powershell
uv sync --extra dev
uv run python -m logic_analyzer_mcp --http --port 10985
```

Health check: `http://127.0.0.1:10985/health`

## Option C - With sigrok hardware

1. Complete Option A
2. Install PulseView (includes sigrok-cli) from https://sigrok.org/wiki/Downloads
3. Verify CLI:

```powershell
sigrok-cli --scan
```

4. Connect LA (e.g. Hantek 6022BL in LA mode), then:

```
la_device(operation="list")
la_device(operation="connect", device_id="sigrok:fx2lafw:...")
```

5. Optional env override:

```powershell
$env:LOGIC_ANALYZER_MCP_SIGROK_CLI = "C:\Program Files\sigrok\sigrok-cli.exe"
```

## Simulator-only (no hardware)

No extra steps. Default backend falls back to simulator:

```
la_device(operation="connect", device_id="sim-la-001")
```

## Webapp

```powershell
just webapp
```

Opens backend on **10985** and Vite on **10987**.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| `sigrok-cli not found` | Install PulseView; set `LOGIC_ANALYZER_MCP_SIGROK_CLI` |
| No devices in list | Check USB, LA mode (6022BL H/P button), Zadig driver |
| Stdio hangs | Logging goes to stderr; set `LOGIC_ANALYZER_ALLOW_LOGGING=1` for debug |
| Import errors | `uv sync --extra dev` from repo root |

## Anti-patterns

- Do not commit `.env` with device serials
- Do not use Linux-only shell syntax in PowerShell scripts
- Do not expect scope mode on 6022BL — flip to LA mode for sigrok fx2lafw
