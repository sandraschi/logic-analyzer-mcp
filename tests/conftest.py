"""Pytest fixtures for logic-analyzer-mcp."""

import pytest

from logic_analyzer_mcp.services import registry


@pytest.fixture(autouse=True)
def reset_registry():
    """Reset global session state between tests."""
    registry._session = None  # type: ignore[attr-defined]
    registry._last_capture = None  # type: ignore[attr-defined]
    registry._last_decode = None  # type: ignore[attr-defined]
    yield
    registry._session = None  # type: ignore[attr-defined]
    registry._last_capture = None  # type: ignore[attr-defined]
    registry._last_decode = None  # type: ignore[attr-defined]
