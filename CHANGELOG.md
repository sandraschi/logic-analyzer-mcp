# Changelog

## Unreleased

### Added

- Tauri 2.0 native wrapper (`native/`) — embedded PyInstaller backend, single NSIS installer
- Webapp pages: Device, Configure, Trigger, Logs + FloatingChat assistant
- Activity logging (`activity_log.py`, opt-in via `LOGIC_ANALYZER_ALLOW_LOGGING`)
- Ollama override via `OLLAMA_BASE_URL` in webapp backend

### Fixed

- Bundled `.env.example` instead of `.env` in NSIS resources (BUG-013 credentials leak)
- ASCII/Unicode cleanup in PowerShell build scripts

### Changed

- Unified transport config (`transport.py`: stdio/http/sse via `LOGIC_ANALYZER_MCP_TRANSPORT`)
- CI switched to reusable fleet workflow (tag-only trigger)
- Enhanced trace + decode webapp views

## 0.1.0 — 2026-06-08

### Added

- FastMCP 3.2+ server with six portmanteau tools
- Simulator and sigrok backends
- Fleet webapp (trace + decode viewers) on ports 10985/10988
- UART/I2C/SPI decode stubs (simulator) and sigrok-cli decode (hardware)
- VCD/CSV/JSON export
- Fleet documentation: PRD, HARDWARE, BACKENDS, FLEET_INTEGRATION
- Discovery: `llms.txt`, `llms-full.txt`, `glama.json`
- MCPB package: `manifest.json`, `just mcpb-pack` → `dist/logic-analyzer-mcp-v0.1.0.mcpb`
- CI workflow (Windows, ruff, pytest, biome)
