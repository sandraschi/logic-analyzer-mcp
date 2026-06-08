from __future__ import annotations

from typing import Any

from logic_analyzer_mcp.models.capture import ChannelLogicCapture, DecodeResult, LogicCapture, TriggerConfig
from logic_analyzer_mcp.models.device import DeviceCapabilities, DeviceInfo
from logic_analyzer_mcp.services.backends.base import LogicAnalyzerBackend

COMMON_DECODERS = ["uart", "i2c", "spi", "parallel", "pwm"]


class SimulatorBackend(LogicAnalyzerBackend):
    name = "simulator"

    def __init__(self) -> None:
        self._connected_id: str | None = None
        self._channels = [f"D{i}" for i in range(8)]
        self._sample_rate_hz = 1_000_000.0
        self._trigger = TriggerConfig()
        self._pattern = "uart"

    async def list_devices(self) -> list[DeviceInfo]:
        caps = DeviceCapabilities(
            backend="simulator",
            channels=8,
            max_sample_rate_hz=24_000_000,
            supported_decoders=COMMON_DECODERS,
            notes="Synthetic UART/I2C/SPI bitstreams for CI and agent dry-runs.",
        )
        return [
            DeviceInfo(
                device_id="sim-la-001",
                backend="simulator",
                model="Logic Analyzer Simulator",
                driver="simulator",
                channel_labels=self._channels,
                connected=self._connected_id == "sim-la-001",
                capabilities=caps,
            )
        ]

    async def connect(self, device_id: str) -> DeviceInfo:
        devices = await self.list_devices()
        match = next((d for d in devices if d.device_id == device_id), None)
        if match is None:
            raise ValueError(f"Simulator device '{device_id}' not found")
        self._connected_id = device_id
        return match.model_copy(update={"connected": True})

    async def disconnect(self) -> None:
        self._connected_id = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._connected_id:
            return None
        devices = await self.list_devices()
        return next((d for d in devices if d.device_id == self._connected_id), None)

    async def configure(
        self,
        *,
        channels: list[str] | None = None,
        sample_rate_hz: float | None = None,
    ) -> dict[str, str | int | float | list[str]]:
        self._ensure_connected()
        if channels:
            self._channels = channels
        if sample_rate_hz:
            self._sample_rate_hz = sample_rate_hz
        return {"channels": self._channels, "sample_rate_hz": self._sample_rate_hz}

    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig:
        self._ensure_connected()
        self._trigger = trigger
        return trigger

    async def capture(
        self,
        *,
        sample_rate_hz: float,
        sample_count: int,
        channels: list[str] | None = None,
    ) -> LogicCapture:
        self._ensure_connected()
        active = channels or self._channels
        sample_count = max(16, min(sample_count, 1_000_000))
        sample_rate_hz = max(1_000.0, min(sample_rate_hz, 24_000_000))
        samples_by_channel = self._generate_pattern(sample_count, active)
        channel_captures = [
            ChannelLogicCapture(channel_id=ch, samples=samples_by_channel.get(ch, [0] * sample_count)) for ch in active
        ]
        return LogicCapture(
            backend=self.name,
            device_id=self._connected_id or "sim-la-001",
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            channels=channel_captures,
            duration_s=sample_count / sample_rate_hz,
            trigger=self._trigger,
            metadata={"simulated": True, "pattern": self._pattern},
        )

    async def list_decoders(self) -> list[str]:
        return COMMON_DECODERS

    async def decode(
        self,
        capture: LogicCapture,
        *,
        protocol: str,
        options: dict[str, str] | None = None,
    ) -> DecodeResult:
        _ = options
        if protocol == "uart":
            rows = [{"type": "data", "byte": "0x48", "ascii": "H"}, {"type": "data", "byte": "0x69", "ascii": "i"}]
        elif protocol == "i2c":
            rows = [{"type": "start"}, {"type": "address", "value": "0x50"}, {"type": "ack"}, {"type": "stop"}]
        elif protocol == "spi":
            rows = [{"type": "transfer", "mosi": "0x9F", "miso": "0x00"}]
        else:
            rows = [{"type": "info", "message": f"Simulator decode placeholder for {protocol}"}]
        return DecodeResult(protocol=protocol, rows=rows, annotations=[f"simulated:{protocol}"])

    async def get_status(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            "connected": self._connected_id is not None,
            "pattern": self._pattern,
            "channels": self._channels,
        }

    def set_pattern(self, pattern: str) -> None:
        self._pattern = pattern

    def _generate_pattern(self, count: int, channels: list[str]) -> dict[str, list[int]]:
        data: dict[str, list[int]] = {ch: [0] * count for ch in channels}
        if "D0" in data:
            # UART 115200-ish bit pattern: 0x55 preamble on D0
            for i in range(count):
                data["D0"][i] = 1 if (i // 8) % 2 == 0 else 0
        if "D1" in data:
            for i in range(count):
                data["D1"][i] = 1 if i % 16 < 8 else 0
        if "D2" in data and "D3" in data:
            for i in range(count):
                data["D2"][i] = 1 if i % 4 < 2 else 0
                data["D3"][i] = data["D2"][i] ^ (1 if i % 8 >= 4 else 0)
        return data

    def _ensure_connected(self) -> None:
        if not self._connected_id:
            raise RuntimeError("No simulator device connected. Use la_device(operation='connect').")
