from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

TriggerMode = Literal["auto", "normal", "single", "off"]


class TriggerConfig(BaseModel):
    mode: TriggerMode = "auto"
    channel: str = "D0"
    pattern: str = "rising"
    level: int = 1


class ChannelLogicCapture(BaseModel):
    channel_id: str
    samples: list[int]


class LogicCapture(BaseModel):
    backend: str
    device_id: str
    sample_rate_hz: float
    sample_count: int
    channels: list[ChannelLogicCapture]
    duration_s: float
    trigger: TriggerConfig | None = None
    metadata: dict[str, str | int | float | bool] = Field(default_factory=dict)


class DecodeResult(BaseModel):
    protocol: str
    rows: list[dict[str, Any]]
    annotations: list[str] = Field(default_factory=list)
    source_capture: str | None = None
