"""Unit tests for la_help tool."""

import pytest

from logic_analyzer_mcp.tools.portmanteau.help import la_help


def _tool_payload(result) -> dict:
    content = result.content
    if isinstance(content, dict):
        return content
    if isinstance(content, list) and content:
        item = content[0]
        if hasattr(item, "text"):
            import json

            return json.loads(item.text)
    raise AssertionError(f"Unexpected tool result shape: {type(content)}")


@pytest.mark.asyncio
async def test_la_help_discover():
    result = await la_help(operation="discover")
    payload = _tool_payload(result)
    assert payload["success"] is True
    assert payload["count"] == 6


@pytest.mark.asyncio
async def test_la_help_quickstart():
    result = await la_help(operation="quickstart")
    payload = _tool_payload(result)
    assert payload["success"] is True
    assert "steps" in payload["data"]
