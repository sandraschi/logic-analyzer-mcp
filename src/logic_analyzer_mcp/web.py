"""REST API for logic-analyzer-mcp webapp."""

from __future__ import annotations

import json
from typing import Any

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from logic_analyzer_mcp import __version__
from logic_analyzer_mcp.capabilities import build_capabilities
from logic_analyzer_mcp.config import get_settings
from logic_analyzer_mcp.services.registry import get_last_capture, get_last_decode, get_session


def setup_webapp(app: FastAPI, mcp: Any) -> None:
    """Register REST routes on the FastAPI application."""

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok", "version": __version__, "server": "logic-analyzer-mcp"}

    @app.get("/api/status")
    async def api_status() -> dict[str, Any]:
        settings = get_settings()
        session = get_session()
        tools = await mcp.list_tools()
        tool_names = [t.name for t in tools]
        backend = session.backend
        connected = None
        if backend is not None:
            device = await backend.get_connected_device()
            connected = device.model_dump(mode="json") if device else None
        return {
            "status": "ok",
            "version": __version__,
            "tool_count": len(tools),
            "tools": tool_names,
            "active_backend": session.backend_name,
            "connected_device": connected,
            "capture_dir": str(settings.capture_dir),
            "capabilities": {
                "prompts": True,
                "resources": True,
                "simulator": True,
                "sigrok": True,
                "decode": True,
            },
        }

    @app.get("/api/capabilities")
    async def api_capabilities() -> dict[str, Any]:
        return await build_capabilities(mcp)

    @app.get("/api/tools")
    async def api_tools() -> dict[str, Any]:
        tools = await mcp.list_tools()
        return {
            "tools": [
                {
                    "name": t.name,
                    "description": t.description or "",
                    "inputSchema": t.parameters,
                }
                for t in tools
            ]
        }

    @app.post("/api/tools/{name}/call")
    async def api_tool_call(name: str, body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        try:
            result = await mcp.call_tool(name, body.get("arguments", {}))
            content = result.content if hasattr(result, "content") else result
            if isinstance(content, list) and content:
                item = content[0]
                text = item.text if hasattr(item, "text") else str(item)
                try:
                    parsed = json.loads(text)
                    return {"success": True, "data": parsed}
                except (json.JSONDecodeError, TypeError):
                    return {"success": True, "data": text}
            return {"success": True, "data": content}
        except Exception as exc:
            return JSONResponse({"success": False, "message": str(exc)}, status_code=500)

    @app.get("/api/capture/last")
    async def api_capture_last() -> dict[str, Any]:
        capture = get_last_capture()
        if capture is None:
            return {"success": False, "message": "No capture in memory"}
        step = max(1, capture.sample_count // 500)
        return {
            "success": True,
            "data": {
                "capture": capture.model_dump(mode="json"),
                "preview": {
                    "step": step,
                    "channels": {ch.channel_id: ch.samples[::step] for ch in capture.channels},
                },
            },
        }

    @app.post("/api/capture/run")
    async def api_capture_run(body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        args = {
            "operation": "single",
            "sample_rate_hz": body.get("sample_rate_hz", 1_000_000),
            "sample_count": body.get("sample_count", 4096),
            "channels": body.get("channels", ["D0", "D1"]),
        }
        return await api_tool_call("la_capture", {"arguments": args})

    @app.get("/api/decode/last")
    async def api_decode_last() -> dict[str, Any]:
        result = get_last_decode()
        if result is None:
            return {"success": False, "message": "No decode in memory"}
        return {"success": True, "data": result.model_dump(mode="json")}

    @app.post("/api/decode/run")
    async def api_decode_run(body: dict[str, Any]) -> JSONResponse | dict[str, Any]:
        protocol = body.get("protocol", "uart")
        operation = body.get("operation", protocol if protocol in ("uart", "i2c", "spi") else "run")
        args: dict[str, Any] = {"operation": operation, "protocol": protocol}
        for key in ("rx", "tx", "sda", "scl", "clk", "mosi", "miso"):
            if key in body:
                args[key] = body[key]
        return await api_tool_call("la_decode", {"arguments": args})
