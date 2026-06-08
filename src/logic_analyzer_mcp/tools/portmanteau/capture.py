"""la_capture portmanteau - acquisition and export."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.config import get_settings
from logic_analyzer_mcp.services.registry import get_last_capture, get_session, set_last_capture
from logic_analyzer_mcp.utils.export import (
    default_capture_filename,
    export_capture_csv,
    export_capture_summary,
    export_capture_vcd,
)


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": False, "destructiveHint": False})
async def la_capture(
    operation: Annotated[
        Literal["single", "preview", "export_csv", "export_vcd", "export_summary", "last"],
        Field(description="Capture operation."),
    ],
    sample_rate_hz: Annotated[float, Field(description="Sample rate in Hz.", gt=0)] = 1_000_000,
    sample_count: Annotated[int, Field(description="Number of samples to acquire.", ge=16, le=1_000_000)] = 4096,
    channels: Annotated[list[str] | None, Field(description="Channels to capture.")] = None,
    filename: Annotated[str | None, Field(description="Optional export filename stem.")] = None,
) -> ToolResult:
    """Acquire digital traces and export capture data.

    ## Examples
    - la_capture(operation="single", sample_rate_hz=1000000, sample_count=4096)
    - la_capture(operation="export_vcd")
    """
    session = get_session()
    settings = get_settings()

    try:
        if operation == "last":
            capture = get_last_capture()
            if capture is None:
                raise RuntimeError("No capture in memory. Run operation='single' first.")
            return ToolResult(
                content={
                    "success": True,
                    "operation": operation,
                    "data": capture.model_dump(mode="json"),
                }
            )

        if operation in ("export_csv", "export_vcd", "export_summary", "preview"):
            capture = get_last_capture()
            if capture is None:
                raise RuntimeError("No capture in memory. Run operation='single' first.")

            stem = filename or default_capture_filename()
            capture_dir = settings.capture_dir
            capture_dir.mkdir(parents=True, exist_ok=True)

            if operation == "export_csv":
                path = export_capture_csv(capture, capture_dir / f"{stem}.csv")
                return ToolResult(
                    content={
                        "success": True,
                        "operation": operation,
                        "data": {"path": str(path), "sample_count": capture.sample_count},
                    }
                )

            if operation == "export_vcd":
                path = export_capture_vcd(capture, capture_dir / f"{stem}.vcd")
                return ToolResult(
                    content={
                        "success": True,
                        "operation": operation,
                        "data": {"path": str(path), "sample_count": capture.sample_count},
                    }
                )

            if operation == "export_summary":
                path = export_capture_summary(capture, capture_dir / f"{stem}.json")
                return ToolResult(
                    content={
                        "success": True,
                        "operation": operation,
                        "data": {"path": str(path), "sample_count": capture.sample_count},
                    }
                )

            step = max(1, capture.sample_count // 200)
            preview = {
                "sample_rate_hz": capture.sample_rate_hz,
                "sample_count": capture.sample_count,
                "step": step,
                "channels": {ch.channel_id: ch.samples[::step] for ch in capture.channels},
            }
            return ToolResult(content={"success": True, "operation": operation, "data": preview})

        backend = session.backend
        if backend is None:
            backend = await session.resolve_backend()
            default_id = "sim-la-001" if backend.name == "simulator" else "sigrok:none"
            await backend.connect(default_id)

        active_channels = channels or ["D0", "D1"]
        capture = await backend.capture(
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            channels=active_channels,
        )
        set_last_capture(capture)

        step = max(1, sample_count // 100)
        data = {
            "capture": capture.model_dump(mode="json"),
            "preview": {
                "step": step,
                "channels": {ch.channel_id: ch.samples[::step] for ch in capture.channels},
            },
            "export_hint": "Use la_capture(operation='export_vcd') for PulseView import.",
            "capture_dir": str(Path(settings.capture_dir)),
        }
        return ToolResult(content={"success": True, "operation": operation, "data": data})
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
