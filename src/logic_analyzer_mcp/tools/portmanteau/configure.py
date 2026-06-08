"""la_configure portmanteau - channel and sample rate setup."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.services.backends.simulator import SimulatorBackend
from logic_analyzer_mcp.services.registry import get_session


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def la_configure(
    operation: Annotated[
        Literal["channels", "sample_rate", "get", "simulator_pattern"],
        Field(description="Configuration operation."),
    ],
    channels: Annotated[list[str] | None, Field(description="Active digital channels (e.g. D0-D7).")] = None,
    sample_rate_hz: Annotated[float | None, Field(description="Target sample rate in Hz.", gt=0)] = None,
    pattern: Annotated[str | None, Field(description="Simulator pattern: uart, i2c, spi.")] = None,
) -> ToolResult:
    """Configure logic analyzer channels and sample rate.

    ## Examples
    - la_configure(operation="channels", channels=["D0", "D1", "D2"])
    - la_configure(operation="sample_rate", sample_rate_hz=24000000)
    """
    session = get_session()

    try:
        backend = session.backend
        if backend is None:
            backend = await session.resolve_backend()
            default_id = "sim-la-001" if backend.name == "simulator" else "sigrok:none"
            await backend.connect(default_id)

        if operation == "get":
            status = await backend.get_status()
            return ToolResult(content={"success": True, "operation": operation, "data": status})

        if operation == "simulator_pattern":
            if not isinstance(backend, SimulatorBackend):
                raise ValueError("simulator_pattern only applies to simulator backend")
            if not pattern:
                raise ValueError("pattern is required")
            backend.set_pattern(pattern)
            return ToolResult(content={"success": True, "operation": operation, "data": {"pattern": pattern}})

        if operation == "channels":
            if not channels:
                raise ValueError("channels is required")
            data = await backend.configure(channels=channels)
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "sample_rate":
            if sample_rate_hz is None:
                raise ValueError("sample_rate_hz is required")
            data = await backend.configure(sample_rate_hz=sample_rate_hz)
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
