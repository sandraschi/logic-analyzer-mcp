"""Shared FastMCP instance for logic-analyzer-mcp."""

from __future__ import annotations

import json
import os
import sys
from contextlib import asynccontextmanager

from fastmcp import FastMCP
from fastmcp.prompts import Message

from logic_analyzer_mcp.config import get_settings
from logic_analyzer_mcp.services.registry import clear_services, get_last_capture, get_last_decode, get_session
from logic_analyzer_mcp.utils.logger import get_logger

if os.name == "nt":
    try:
        import msvcrt

        msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
        msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)
    except (OSError, AttributeError):
        pass

_is_stdio_mode = not sys.stdout.isatty()
if os.getenv("LOGIC_ANALYZER_ALLOW_LOGGING", "").lower() in ("1", "true", "yes") or any(
    "pytest" in (arg or "") for arg in sys.argv
):
    _is_stdio_mode = False


@asynccontextmanager
async def _la_lifespan(app):
    """FastMCP lifespan hook - startup probe and clean shutdown."""
    logger = get_logger(__name__)
    settings = get_settings()
    session = get_session()

    try:
        backend = await session.resolve_backend()
        devices = await backend.list_devices()
        logger.info(
            "Startup probe: backend=%s devices=%d capture_dir=%s",
            backend.name,
            len(devices),
            settings.capture_dir,
        )
        settings.capture_dir.mkdir(parents=True, exist_ok=True)
        app.state.settings = settings
        app.state.session = session
    except Exception as exc:
        logger.warning("Startup probe failed (simulator fallback may still work): %s", exc)

    yield

    await clear_services()
    app.state.session = None


mcp = FastMCP(
    "LogicAnalyzerMCP",
    instructions=(
        "LogicAnalyzerMCP is a FastMCP 3.2+ server for USB logic analyzers via sigrok and simulator backends. "
        "Portmanteau tools: la_device, la_configure, la_trigger, la_capture, la_decode, la_help. "
        "Default workflow: la_device(operation='list') -> connect -> configure -> capture -> decode. "
        "Resources: resource://la/capabilities, resource://la/quickstart, resource://la/last_capture."
    ),
    lifespan=_la_lifespan,
    on_duplicate="replace",
    strict_input_validation=True,
)


@mcp.resource("resource://la/capabilities")
def la_capabilities_resource() -> str:
    return """# logic-analyzer-mcp capabilities

## Tools
- la_device: list, connect, disconnect, status, capabilities, backends
- la_configure: channels, sample_rate, get, simulator_pattern
- la_trigger: set, get
- la_capture: single, preview, export_csv, export_vcd, export_summary, last
- la_decode: list, run, last, uart, i2c, spi
- la_help: discover, tool_help, status, quickstart, faq, hardware_guide

## Backends
| Backend | Hardware | Requirement |
|---------|----------|-------------|
| simulator | none | built-in |
| sigrok | Hantek 6022BL (LA mode), DSLogic, FX2 clones | sigrok-cli on PATH |

## Fleet pair
Use with oscilloscope-mcp for mixed-signal bring-up (analog rails + digital buses).
"""


@mcp.resource("resource://la/quickstart")
def la_quickstart_resource() -> str:
    return """# logic-analyzer-mcp quickstart

1. la_help(operation="quickstart")
2. la_device(operation="list")
3. la_device(operation="connect", device_id="sim-la-001")
4. la_configure(operation="channels", channels=["D0", "D1"])
5. la_trigger(operation="set", channel="D0", pattern="rising")
6. la_capture(operation="single", sample_rate_hz=1000000, sample_count=4096)
7. la_decode(operation="uart", rx="D0")
8. la_capture(operation="export_vcd")
"""


@mcp.resource("resource://la/last_capture")
def la_last_capture_resource() -> str:
    capture = get_last_capture()
    if capture is None:
        return json.dumps({"status": "empty", "message": "No capture yet. Run la_capture(operation='single')."})
    step = max(1, capture.sample_count // 200)
    payload = {
        "status": "ok",
        "backend": capture.backend,
        "device_id": capture.device_id,
        "sample_rate_hz": capture.sample_rate_hz,
        "sample_count": capture.sample_count,
        "channels": [ch.channel_id for ch in capture.channels],
        "preview": {
            "step": step,
            "channels": {ch.channel_id: ch.samples[::step] for ch in capture.channels},
        },
        "last_decode": get_last_decode().model_dump(mode="json") if get_last_decode() else None,
    }
    return json.dumps(payload, indent=2)


@mcp.prompt()
def la_bringup_guide() -> list[Message]:
    """Guide for logic analyzer bring-up and protocol decode."""
    return [
        Message(
            "Use la_device(operation='list') to find USB logic analyzers. "
            "For dry-runs without hardware, connect to sim-la-001. "
            "After capture, la_decode(operation='uart') decodes serial traffic on D0.",
            role="user",
        )
    ]


if _is_stdio_mode:
    import logging

    logging.basicConfig(
        level=get_settings().log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stderr,
    )
