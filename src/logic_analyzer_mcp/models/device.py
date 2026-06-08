from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

BackendType = Literal["simulator", "sigrok"]


class DeviceCapabilities(BaseModel):
    backend: BackendType
    channels: int = Field(ge=1, le=32)
    max_sample_rate_hz: float = Field(gt=0)
    supported_decoders: list[str] = Field(default_factory=list)
    notes: str | None = None


class DeviceInfo(BaseModel):
    device_id: str
    backend: BackendType
    model: str
    driver: str | None = None
    serial: str | None = None
    connected: bool = False
    channel_labels: list[str] = Field(default_factory=list)
    capabilities: DeviceCapabilities
    driver_status: str = "available"
    driver_hint: str | None = None
