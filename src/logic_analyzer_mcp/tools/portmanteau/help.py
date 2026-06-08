"""la_help portmanteau - discovery and documentation."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.services.registry import get_session

_TOOLS_CATALOG: dict[str, dict[str, Any]] = {
    "la_device": {
        "category": "device",
        "operations": ["list", "connect", "disconnect", "status", "capabilities", "backends"],
        "description": "Discover USB logic analyzers, connect sessions, inspect backend health.",
    },
    "la_configure": {
        "category": "configure",
        "operations": ["channels", "sample_rate", "get", "simulator_pattern"],
        "description": "Set active channels, sample rate, and simulator bit patterns.",
    },
    "la_trigger": {
        "category": "trigger",
        "operations": ["set", "get"],
        "description": "Configure digital trigger channel, edge, and mode.",
    },
    "la_capture": {
        "category": "capture",
        "operations": ["single", "preview", "export_csv", "export_vcd", "export_summary", "last"],
        "description": "Acquire digital traces and export CSV/VCD/JSON.",
    },
    "la_decode": {
        "category": "decode",
        "operations": ["list", "run", "last", "uart", "i2c", "spi"],
        "description": "Decode UART, I2C, SPI and other sigrok protocols.",
    },
    "la_help": {
        "category": "help",
        "operations": ["discover", "tool_help", "status", "quickstart", "faq", "hardware_guide"],
        "description": "Tool discovery, quickstart, FAQ, and hardware buying guide.",
    },
}


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def la_help(
    operation: Annotated[
        Literal["discover", "tool_help", "status", "quickstart", "faq", "hardware_guide"],
        Field(description="Help operation."),
    ],
    tool_name: Annotated[str | None, Field(description="Tool name for tool_help.")] = None,
    topic: Annotated[str | None, Field(description="FAQ topic filter.")] = None,
) -> ToolResult:
    """Help, discovery, and hardware guidance for logic-analyzer-mcp."""
    try:
        if operation == "discover":
            catalog = [{"name": name, **meta} for name, meta in _TOOLS_CATALOG.items()]
            if topic:
                catalog = [item for item in catalog if item["category"] == topic]
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": catalog,
                    "count": len(catalog),
                }
            )

        if operation == "tool_help":
            if not tool_name:
                raise ValueError("tool_name is required for tool_help")
            tool = _TOOLS_CATALOG.get(tool_name)
            if not tool:
                raise ValueError(f"Tool '{tool_name}' not found")
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {"name": tool_name, **tool},
                }
            )

        if operation == "status":
            session = get_session()
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "server": "logic-analyzer-mcp",
                        "version": "0.1.0",
                        "tools_registered": len(_TOOLS_CATALOG),
                        "active_backend": session.backend_name,
                    },
                }
            )

        if operation == "quickstart":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "steps": [
                            "1. la_device(operation='list')",
                            "2. la_device(operation='connect', device_id='sim-la-001')",
                            "3. la_configure(operation='channels', channels=['D0','D1'])",
                            "4. la_trigger(operation='set', channel='D0', pattern='rising')",
                            "5. la_capture(operation='single', sample_rate_hz=1000000, sample_count=4096)",
                            "6. la_decode(operation='uart', rx='D0')",
                            "7. la_capture(operation='export_vcd')",
                        ],
                    },
                }
            )

        if operation == "faq":
            faq = [
                {
                    "q": "Can I use this without hardware?",
                    "a": "Yes. Connect to sim-la-001 and use the simulator backend.",
                    "topic": "simulator",
                },
                {
                    "q": "What is sigrok?",
                    "a": "Open-source signal analysis stack. Install PulseView or sigrok-cli for USB LA support.",
                    "topic": "sigrok",
                },
                {
                    "q": "Hantek 6022BL as logic analyzer?",
                    "a": "Flip H/P to LA mode; shows as Saleae Logic VID. Use fx2lafw driver via sigrok (8ch @ 24 MHz).",
                    "topic": "hardware",
                },
                {
                    "q": "Pair with oscilloscope-mcp?",
                    "a": "Yes — scope for analog rails, LA for digital buses during MCU/FPGA bring-up.",
                    "topic": "fleet",
                },
            ]
            if topic:
                faq = [item for item in faq if item["topic"] == topic]
            return ToolResult(content={"success": True, "operation": operation, "data": faq})

        if operation == "hardware_guide":
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": {
                        "recommendations": [
                            {
                                "tier": "budget_hack",
                                "model": "Hantek 6022BL (LA mode)",
                                "price_usd": "40-80",
                                "channels": "8 @ 24 MHz",
                                "backend": "sigrok (fx2lafw)",
                                "notes": "Same USB dongle as 6022BE scope; flip H/P button for LA mode.",
                            },
                            {
                                "tier": "dedicated_la",
                                "model": "DSLogic / DSLogic Plus",
                                "price_usd": "80-150",
                                "channels": "16 @ 400 MHz (Plus)",
                                "backend": "sigrok (dslogic)",
                                "notes": "Purpose-built LA with good PulseView support.",
                            },
                            {
                                "tier": "fx2_clone",
                                "model": "Saleae Logic clone (FX2)",
                                "price_usd": "10-30",
                                "channels": "8 @ 24 MHz",
                                "backend": "sigrok (fx2lafw)",
                                "notes": "Cheap AliExpress boards; quality varies.",
                            },
                        ],
                        "avoid": "Closed Windows-only LA software with no sigrok driver.",
                    },
                }
            )

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
