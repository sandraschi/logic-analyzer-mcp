# logic-analyzer-mcp

[![MIT License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](pyproject.toml)
[![FastMCP 3.2+](https://img.shields.io/badge/FastMCP-3.2+-green.svg)](pyproject.toml)

AI-driven USB logic analyzer control via **FastMCP 3.2**. Capture digital traces with sigrok or the built-in simulator, decode UART/I2C/SPI, and export VCD for PulseView.

## How it runs

| Mode | Hardware | When |
|------|----------|------|
| **Simulator (default)** | None | Development, CI, agent dry-runs |
| **sigrok** | Hantek 6022BL (LA mode), DSLogic, FX2 clones | Production bench with sigrok-cli |

The MCP server does not bundle sigrok. Install PulseView or sigrok-cli separately, then connect your USB LA.

## Hands-in / Hands-out

| Direction | Artifacts | Notes |
|-----------|-----------|-------|
| **Hands-in** | `device_id`, channels, trigger | Via `la_device`, `la_configure`, `la_trigger` |
| **Hands-out** | Trace preview (downsampled JSON) | `la_capture(operation="single")` |
| **Hands-out** | CSV, VCD, JSON summary | `la_capture(operation="export_vcd")` in `LOGIC_ANALYZER_MCP_CAPTURE_DIR` |
| **Hands-out** | Protocol decode rows | `la_decode(operation="uart")` |

### Fleet pipelines

| Partner MCP | Workflow |
|-------------|----------|
| [oscilloscope-mcp](https://github.com/sandraschi/oscilloscope-mcp) | Mixed-signal bring-up (analog + digital) |
| [kicad-mcp](https://github.com/sandraschi/kicad-mcp) | Verify SPI/I2C after PCB bring-up |
| [chip-design-mcp](https://github.com/sandraschi/chip-design-mcp) | Debug FPGA/MCU buses |

## Quick Start

```powershell
Set-Location D:\Dev\repos\logic-analyzer-mcp
uv sync --extra dev
just webapp
# Open http://127.0.0.1:10987
```

STDIO-only (Cursor MCP):

```powershell
just serve
```

Dry-run without hardware:

```
la_device(operation="connect", device_id="sim-la-001")
la_capture(operation="single", sample_rate_hz=1000000, sample_count=4096)
la_decode(operation="uart", rx="D0")
```

## Cursor MCP config

Add to `C:\Users\sandr\.cursor\mcp.json`:

```json
"logic-analyzer-mcp": {
  "command": "C:/Users/sandr/.local/bin/uv.exe",
  "args": [
    "--directory",
    "D:/Dev/repos/logic-analyzer-mcp",
    "run",
    "python",
    "-m",
    "logic_analyzer_mcp",
    "--stdio"
  ],
  "env": {
    "FASTMCP_BANNER": "0",
    "FASTMCP_UPDATE_CHECK": "0",
    "PYTHONUNBUFFERED": "1",
    "LOGIC_ANALYZER_MCP_BACKEND": "auto"
  }
}
```

Restart Cursor after editing `mcp.json`.

## Tools

| Tool | Operations |
|------|------------|
| `la_device` | list, connect, disconnect, status, capabilities, backends |
| `la_configure` | channels, sample_rate, get, simulator_pattern |
| `la_trigger` | set, get |
| `la_capture` | single, preview, export_csv, export_vcd, export_summary, last |
| `la_decode` | list, run, last, uart, i2c, spi |
| `la_help` | discover, tool_help, status, quickstart, faq, hardware_guide |

## Webapp

| Port | Role |
|------|------|
| 10985 | Backend (FastAPI + MCP `/mcp`) |
| 10987 | Frontend (Vite React — trace + decode viewers) |

```powershell
just webapp
```

## Documentation

- [INSTALL.md](INSTALL.md) — setup paths
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system design
- [docs/TOOLS.md](docs/TOOLS.md) — portmanteau reference
- [docs/HARDWARE.md](docs/HARDWARE.md) — LA buying guide
- [docs/BACKENDS.md](docs/BACKENDS.md) — sigrok + simulator
- [llms.txt](llms.txt) — agent discovery index

## License

MIT — see [LICENSE](LICENSE).
