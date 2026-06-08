"""Integration test for simulator capture and decode flow."""

import pytest

from logic_analyzer_mcp.services.registry import get_last_capture, get_last_decode, set_last_capture, set_last_decode
from logic_analyzer_mcp.services.session import LogicSession


@pytest.mark.integration
@pytest.mark.asyncio
async def test_end_to_end_simulator_flow():
    session = LogicSession()
    backend = session.get_backend("simulator")
    await backend.connect("sim-la-001")
    await backend.configure(channels=["D0", "D1"], sample_rate_hz=1_000_000)

    capture = await backend.capture(
        sample_rate_hz=1_000_000,
        sample_count=512,
        channels=["D0", "D1"],
    )
    set_last_capture(capture)
    assert capture.sample_count == 512
    assert get_last_capture() is not None

    decoded = await backend.decode(capture, protocol="i2c")
    set_last_decode(decoded)
    assert decoded.protocol == "i2c"
    assert get_last_decode() is not None
