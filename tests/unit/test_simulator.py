"""Unit tests for simulator backend."""

import pytest

from logic_analyzer_mcp.services.backends.simulator import SimulatorBackend
from logic_analyzer_mcp.services.registry import set_last_capture


@pytest.mark.asyncio
async def test_simulator_list_and_connect():
    backend = SimulatorBackend()
    devices = await backend.list_devices()
    assert len(devices) == 1
    assert devices[0].device_id == "sim-la-001"

    connected = await backend.connect("sim-la-001")
    assert connected.connected is True


@pytest.mark.asyncio
async def test_simulator_capture_and_decode():
    backend = SimulatorBackend()
    await backend.connect("sim-la-001")
    capture = await backend.capture(
        sample_rate_hz=1_000_000,
        sample_count=256,
        channels=["D0", "D1"],
    )
    assert capture.sample_count == 256
    assert len(capture.channels) == 2
    set_last_capture(capture)

    result = await backend.decode(capture, protocol="uart")
    assert result.protocol == "uart"
    assert result.rows
