"""la_device portmanteau - discovery, connection, and status."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.config import get_settings
from logic_analyzer_mcp.services.registry import get_session


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def la_device(
    operation: Annotated[
        Literal["list", "connect", "disconnect", "status", "capabilities", "backends"],
        Field(description="Device management operation."),
    ],
    device_id: Annotated[
        str | None, Field(description="Device ID for connect (e.g. sim-la-001, sigrok:fx2lafw:...).")
    ] = None,
    backend: Annotated[str | None, Field(description="Force backend: simulator or sigrok.")] = None,
) -> ToolResult:
    """Discover, connect, and manage USB logic analyzer devices.

    ## Return Format
    {"success": bool, "operation": str, "data": {...}}

    ## Examples
    - la_device(operation="list")
    - la_device(operation="connect", device_id="sim-la-001")
    - la_device(operation="status")
    """
    session = get_session()
    settings = get_settings()

    try:
        if operation == "list":
            devices = await session.list_all_devices()
            data = {
                "devices": [d.model_dump(mode="json") for d in devices],
                "count": len(devices),
                "preferred_backend": settings.backend,
            }
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "backends":
            data = {"backends": session.list_backend_names(), "active": session.backend_name}
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "connect":
            if not device_id:
                raise ValueError("device_id is required for connect")
            device = await session.connect(device_id, backend=backend)
            data = device.model_dump(mode="json")
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "disconnect":
            await session.disconnect()
            return ToolResult(content={"success": True, "operation": operation, "data": {"connected": False}})

        if operation == "status":
            active = session.backend
            if active is None:
                data: dict[str, Any] = {"connected": False, "backend": None}
            else:
                status = await active.get_status()
                connected = await active.get_connected_device()
                data = {
                    "connected": connected is not None,
                    "backend": session.backend_name,
                    "device": connected.model_dump(mode="json") if connected else None,
                    "status": status,
                    "capture_dir": str(settings.capture_dir),
                }
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        if operation == "capabilities":
            active = session.backend or await session.resolve_backend()
            connected = await active.get_connected_device()
            if connected:
                data = connected.capabilities.model_dump(mode="json")
            else:
                devices = await active.list_devices()
                data = devices[0].capabilities.model_dump(mode="json") if devices else {}
            return ToolResult(content={"success": True, "operation": operation, "data": data})

        raise ValueError(f"Unknown operation: {operation}")
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
