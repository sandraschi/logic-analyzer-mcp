"""la_trigger portmanteau - digital trigger configuration."""

from __future__ import annotations

from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.models.capture import TriggerConfig
from logic_analyzer_mcp.services.registry import get_session


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def la_trigger(
    operation: Annotated[Literal["set", "get"], Field(description="Trigger operation.")],
    channel: Annotated[str | None, Field(description="Trigger channel (e.g. D0).")] = None,
    pattern: Annotated[str | None, Field(description="Edge/pattern: rising, falling, high, low.")] = None,
    mode: Annotated[Literal["auto", "normal", "single", "off"] | None, Field(description="Trigger mode.")] = None,
    level: Annotated[int | None, Field(description="Logic level 0 or 1.")] = None,
) -> ToolResult:
    """Configure digital trigger source and pattern.

    ## Examples
    - la_trigger(operation="set", channel="D0", pattern="rising", mode="auto")
    - la_trigger(operation="get")
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

        if operation == "set":
            trigger = TriggerConfig(
                channel=channel or "D0",
                pattern=pattern or "rising",
                mode=mode or "auto",
                level=level if level is not None else 1,
            )
            saved = await backend.configure_trigger(trigger)
            return ToolResult(content={"success": True, "operation": operation, "data": saved.model_dump(mode="json")})

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
