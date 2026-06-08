from __future__ import annotations

from abc import ABC, abstractmethod

from logic_analyzer_mcp.models.capture import DecodeResult, LogicCapture, TriggerConfig
from logic_analyzer_mcp.models.device import DeviceInfo


class LogicAnalyzerBackend(ABC):
    name: str

    @abstractmethod
    async def list_devices(self) -> list[DeviceInfo]: ...

    @abstractmethod
    async def connect(self, device_id: str) -> DeviceInfo: ...

    @abstractmethod
    async def disconnect(self) -> None: ...

    @abstractmethod
    async def get_connected_device(self) -> DeviceInfo | None: ...

    @abstractmethod
    async def configure(
        self,
        *,
        channels: list[str] | None = None,
        sample_rate_hz: float | None = None,
    ) -> dict[str, str | int | float | list[str]]: ...

    @abstractmethod
    async def configure_trigger(self, trigger: TriggerConfig) -> TriggerConfig: ...

    @abstractmethod
    async def capture(
        self,
        *,
        sample_rate_hz: float,
        sample_count: int,
        channels: list[str] | None = None,
    ) -> LogicCapture: ...

    @abstractmethod
    async def list_decoders(self) -> list[str]: ...

    @abstractmethod
    async def decode(
        self,
        capture: LogicCapture,
        *,
        protocol: str,
        options: dict[str, str] | None = None,
    ) -> DecodeResult: ...

    @abstractmethod
    async def get_status(self) -> dict[str, str | int | float | bool | None]: ...
