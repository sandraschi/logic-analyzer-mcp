# Product Requirements Document — Logic Analyzer MCP

**Version:** 0.1.0  
**Last updated:** 2026-06-08  
**Repo:** https://github.com/sandraschi/logic-analyzer-mcp  
**Fleet pair:** [oscilloscope-mcp](https://github.com/sandraschi/oscilloscope-mcp) (analog rails)

---

## Overview

Logic Analyzer MCP is a **FastMCP 3.2+** server plus React webapp for **USB logic analyzers** via **sigrok-cli** and a built-in **simulator**. Capture digital traces, decode UART/I2C/SPI, export VCD for PulseView.

## Problem statement

- Cheap LA hardware ships with closed Windows apps; sigrok is the open stack.
- Agents need protocol decode and trace export without hand-running PulseView.
- Hantek 6022BL doubles as scope (oscilloscope-mcp) or LA (this repo) — fleet must document both modes.

## Target audience

| Persona | Need |
|---------|------|
| Agent / IDE user | Portmanteau tools, simulator dry-run, decode rows |
| Hardware tinkerer | sigrok fx2lafw (6022BL LA mode), DSLogic |
| Fleet operator | stdio MCP, HTTP :10985, webapp :10987, MCPB package |

## Success metrics

| Metric | Target |
|--------|--------|
| Simulator dry-run | Connect `sim-la-001` → capture → UART decode in &lt;5 tool calls |
| Stdio safety | No stdout logging in default MCP mode |
| Honesty | Missing sigrok-cli returns install guidance |
| Discovery | `llms.txt`, `glama.json`, `GET /api/capabilities` |

## Functional requirements

### MCP tools (portmanteau)

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-TOOL-01 | `la_device` — list, connect, disconnect, status, backends | Done |
| REQ-TOOL-02 | `la_configure` — channels, sample_rate, simulator_pattern | Done |
| REQ-TOOL-03 | `la_trigger` — set, get | Done |
| REQ-TOOL-04 | `la_capture` — single, preview, export_csv/vcd/summary | Done |
| REQ-TOOL-05 | `la_decode` — uart, i2c, spi, list, run | Done |
| REQ-TOOL-06 | `la_help` — discover, quickstart, hardware_guide, faq | Done |

### Backends

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-BE-01 | Simulator with synthetic bus patterns | Done |
| REQ-BE-02 | sigrok-cli scan, capture, decode subprocess | Done |

### Webapp

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-WEB-01 | Dashboard, trace lanes, decode table, tools hub | Done |
| REQ-WEB-02 | Vite proxy `/api` → backend :10985 | Done |
| REQ-WEB-03 | Biome + Ruff in `just lint` | Done |

### Distribution

| ID | Requirement | Status |
|----|-------------|--------|
| REQ-DIST-01 | `manifest.json` + `.mcpb` Claude Desktop bundle | Done |
| REQ-DIST-02 | `glama.json` fleet discovery | Done |
| REQ-DIST-03 | `llms.txt` agent index | Done |

## Non-functional requirements

| Area | Requirement |
|------|-------------|
| Performance | Preview downsampling; cap sample_count at 1M |
| Portability | Windows-first; sigrok via PATH |
| Pairing | Document 6022BL H/P mode vs oscilloscope-mcp scope mode |

## Out of scope (v0.1)

- Bundled sigrok/PulseView installer
- Saleae Logic Pro proprietary protocol
- Real-time streaming decode at full 24 MHz depth

## Fleet pipelines

| Partner | Workflow |
|---------|----------|
| oscilloscope-mcp | Analog rails + digital buses |
| kicad-mcp | SPI/I2C verification after layout |
| chip-design-mcp | FPGA/MCU bus bring-up |
