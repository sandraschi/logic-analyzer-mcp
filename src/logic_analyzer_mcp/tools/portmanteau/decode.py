"""la_decode portmanteau - protocol decoding."""

from __future__ import annotations

from typing import Annotated, Any, Literal

from fastmcp.tools import ToolResult
from pydantic import Field

from logic_analyzer_mcp.app import mcp
from logic_analyzer_mcp.services.registry import get_last_capture, get_last_decode, get_session, set_last_decode


@mcp.tool(version="1.0.0", annotations={"readOnlyHint": True})
async def la_decode(
    operation: Annotated[
        Literal["list", "run", "last", "uart", "i2c", "spi"],
        Field(description="Decode operation."),
    ],
    protocol: Annotated[str | None, Field(description="Decoder protocol name.")] = None,
    rx: Annotated[str | None, Field(description="UART RX channel.")] = None,
    tx: Annotated[str | None, Field(description="UART TX channel.")] = None,
    sda: Annotated[str | None, Field(description="I2C SDA channel.")] = None,
    scl: Annotated[str | None, Field(description="I2C SCL channel.")] = None,
    clk: Annotated[str | None, Field(description="SPI clock channel.")] = None,
    mosi: Annotated[str | None, Field(description="SPI MOSI channel.")] = None,
    miso: Annotated[str | None, Field(description="SPI MISO channel.")] = None,
) -> ToolResult:
    """Decode captured digital traces with sigrok decoders or simulator stubs.

    ## Examples
    - la_decode(operation="list")
    - la_decode(operation="uart", rx="D0")
    - la_decode(operation="i2c", sda="D0", scl="D1")
    """
    session = get_session()

    try:
        if operation == "last":
            result = get_last_decode()
            if result is None:
                raise RuntimeError("No decode in memory. Run operation='uart' or operation='run' first.")
            return ToolResult(content={"success": True, "operation": operation, "data": result.model_dump(mode="json")})

        backend = session.backend
        if backend is None:
            backend = await session.resolve_backend()
            default_id = "sim-la-001" if backend.name == "simulator" else "sigrok:none"
            await backend.connect(default_id)

        if operation == "list":
            decoders = await backend.list_decoders()
            return ToolResult(content={"success": True, "operation": operation, "data": {"decoders": decoders}})

        capture = get_last_capture()
        if capture is None:
            raise RuntimeError("No capture in memory. Run la_capture(operation='single') first.")

        selected_protocol = protocol or (operation if operation in ("uart", "i2c", "spi") else None)
        if operation in ("uart", "i2c", "spi"):
            selected_protocol = operation
        if operation == "run" and not selected_protocol:
            raise ValueError("protocol is required for run")

        options: dict[str, str] = {}
        if rx:
            options["rx"] = rx
        if tx:
            options["tx"] = tx
        if sda:
            options["sda"] = sda
        if scl:
            options["scl"] = scl
        if clk:
            options["clk"] = clk
        if mosi:
            options["mosi"] = mosi
        if miso:
            options["miso"] = miso

        if selected_protocol == "uart" and "rx" not in options:
            options["rx"] = "D0"
        if selected_protocol == "i2c":
            options.setdefault("sda", "D0")
            options.setdefault("scl", "D1")
        if selected_protocol == "spi":
            options.setdefault("clk", "D0")
            options.setdefault("mosi", "D1")
            options.setdefault("miso", "D2")

        if not selected_protocol:
            raise ValueError("protocol is required")

        result = await backend.decode(capture, protocol=selected_protocol, options=options)
        set_last_decode(result)
        data: dict[str, Any] = result.model_dump(mode="json")
        return ToolResult(content={"success": True, "operation": operation, "data": data})
    except Exception as exc:
        return ToolResult(content={"success": False, "operation": operation, "error": str(exc)})
