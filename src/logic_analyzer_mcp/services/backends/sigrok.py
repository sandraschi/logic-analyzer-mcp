from __future__ import annotations

import asyncio
import re
import shutil
from pathlib import Path
from typing import Any

from logic_analyzer_mcp.config import get_settings
from logic_analyzer_mcp.models.capture import ChannelLogicCapture, DecodeResult, LogicCapture, TriggerConfig
from logic_analyzer_mcp.models.device import DeviceCapabilities, DeviceInfo
from logic_analyzer_mcp.services.backends.base import LogicAnalyzerBackend
from logic_analyzer_mcp.utils.export import export_capture_csv


class SigrokBackend(LogicAnalyzerBackend):
    name = "sigrok"

    def __init__(self) -> None:
        self._device_id: str | None = None
        self._driver: str | None = None
        self._channels = [f"D{i}" for i in range(8)]
        self._sample_rate_hz = 1_000_000.0
        self._trigger = TriggerConfig()
        self._cli_error: str | None = None

    def _cli(self) -> str:
        settings = get_settings()
        return settings.sigrok_cli

    async def _run(self, *args: str, timeout: float = 60.0) -> tuple[int, str, str]:
        cli = self._cli()
        if not shutil.which(cli):
            raise RuntimeError(
                f"'{cli}' not found on PATH. Install PulseView/sigrok-cli or set LOGIC_ANALYZER_MCP_SIGROK_CLI."
            )
        proc = await asyncio.create_subprocess_exec(
            cli,
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        try:
            stdout_b, stderr_b = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        except TimeoutError as exc:
            proc.kill()
            raise RuntimeError(f"sigrok-cli timed out: {' '.join(args)}") from exc
        stdout = stdout_b.decode("utf-8", errors="replace")
        stderr = stderr_b.decode("utf-8", errors="replace")
        return proc.returncode or 0, stdout, stderr

    async def list_devices(self) -> list[DeviceInfo]:
        devices: list[DeviceInfo] = []
        try:
            code, stdout, stderr = await self._run("--scan")
            if code != 0:
                self._cli_error = stderr.strip() or stdout.strip()
                return [self._unavailable_device(self._cli_error)]
            for line in stdout.splitlines():
                line = line.strip()
                if not line or "channels" not in line.lower():
                    continue
                device_id = line.split(" - ", maxsplit=1)[0].strip()
                labels = re.findall(r"D\d+", line)
                caps = DeviceCapabilities(
                    backend="sigrok",
                    channels=len(labels) or 8,
                    max_sample_rate_hz=24_000_000,
                    supported_decoders=["uart", "i2c", "spi", "can", "usb"],
                    notes="Requires sigrok-cli and compatible USB driver (fx2lafw, dslogic, etc.).",
                )
                devices.append(
                    DeviceInfo(
                        device_id=f"sigrok:{device_id}",
                        backend="sigrok",
                        model=line,
                        driver=device_id.split(":", maxsplit=1)[0],
                        channel_labels=labels or [f"D{i}" for i in range(8)],
                        connected=self._device_id == f"sigrok:{device_id}",
                        capabilities=caps,
                    )
                )
            if not devices:
                devices.append(
                    DeviceInfo(
                        device_id="sigrok:none",
                        backend="sigrok",
                        model="No sigrok devices detected",
                        channel_labels=[],
                        connected=False,
                        capabilities=DeviceCapabilities(
                            backend="sigrok",
                            channels=8,
                            max_sample_rate_hz=24_000_000,
                            notes="Run sigrok-cli --scan with hardware connected.",
                        ),
                        driver_status="no_devices",
                    )
                )
        except Exception as exc:
            devices.append(self._unavailable_device(str(exc)))
        return devices

    def _unavailable_device(self, hint: str) -> DeviceInfo:
        return DeviceInfo(
            device_id="sigrok:unavailable",
            backend="sigrok",
            model="sigrok backend unavailable",
            channel_labels=[],
            connected=False,
            capabilities=DeviceCapabilities(
                backend="sigrok",
                channels=8,
                max_sample_rate_hz=24_000_000,
                notes=hint,
            ),
            driver_status="unavailable",
            driver_hint=hint,
        )

    async def connect(self, device_id: str) -> DeviceInfo:
        await self.disconnect()
        driver = device_id.removeprefix("sigrok:")
        self._device_id = device_id
        self._driver = driver
        devices = await self.list_devices()
        match = next((d for d in devices if d.device_id == device_id), None)
        if match is None:
            match = DeviceInfo(
                device_id=device_id,
                backend="sigrok",
                model=driver,
                driver=driver.split(":", maxsplit=1)[0],
                channel_labels=self._channels,
                connected=True,
                capabilities=DeviceCapabilities(
                    backend="sigrok",
                    channels=len(self._channels),
                    max_sample_rate_hz=24_000_000,
                ),
            )
        return match.model_copy(update={"connected": True})

    async def disconnect(self) -> None:
        self._device_id = None
        self._driver = None

    async def get_connected_device(self) -> DeviceInfo | None:
        if not self._device_id:
            return None
        devices = await self.list_devices()
        return next((d.model_copy(update={"connected": True}) for d in devices if d.device_id == self._device_id), None)

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
        settings = get_settings()
        capture_dir = settings.capture_dir
        capture_dir.mkdir(parents=True, exist_ok=True)
        csv_path = capture_dir / "sigrok_live_capture.csv"
        driver = self._driver or ""
        channels_arg = ",".join(active)
        rate_arg = f"{int(sample_rate_hz)}Hz"
        code, stdout, stderr = await self._run(
            "-d",
            driver,
            "--channels",
            channels_arg,
            "--samples",
            str(sample_count),
            "--samplerate",
            rate_arg,
            "-O",
            "csv",
            "-o",
            str(csv_path),
        )
        if code != 0 or not csv_path.exists():
            raise RuntimeError(f"sigrok capture failed: {stderr.strip() or stdout.strip()}")
        channel_samples = self._parse_sigrok_csv(csv_path, active, sample_count)
        channel_captures = [ChannelLogicCapture(channel_id=ch, samples=channel_samples[ch]) for ch in active]
        return LogicCapture(
            backend=self.name,
            device_id=self._device_id or "sigrok:unknown",
            sample_rate_hz=sample_rate_hz,
            sample_count=sample_count,
            channels=channel_captures,
            duration_s=sample_count / sample_rate_hz,
            trigger=self._trigger,
            metadata={"driver": driver, "csv_path": str(csv_path)},
        )

    def _parse_sigrok_csv(self, path: Path, channels: list[str], sample_count: int) -> dict[str, list[int]]:
        import csv

        result: dict[str, list[int]] = {ch: [0] * sample_count for ch in channels}
        with path.open(encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            rows = list(reader)
        for idx, row in enumerate(rows[:sample_count]):
            for ch in channels:
                raw = row.get(ch) or row.get(ch.lower()) or "0"
                result[ch][idx] = 1 if str(raw).strip() in {"1", "H", "h", "high", "True"} else 0
        return result

    async def list_decoders(self) -> list[str]:
        try:
            code, stdout, _stderr = await self._run("--list-decoders")
            if code != 0:
                return ["uart", "i2c", "spi"]
            return [
                line.strip().split()[0] for line in stdout.splitlines() if line.strip() and not line.startswith("  ")
            ]
        except Exception:
            return ["uart", "i2c", "spi"]

    async def decode(
        self,
        capture: LogicCapture,
        *,
        protocol: str,
        options: dict[str, str] | None = None,
    ) -> DecodeResult:
        self._ensure_connected()
        settings = get_settings()
        capture_dir = settings.capture_dir
        capture_dir.mkdir(parents=True, exist_ok=True)
        csv_path = capture_dir / "decode_input.csv"
        export_capture_csv(capture, csv_path)
        stack = self._build_decoder_stack(protocol, options or {})
        code, stdout, stderr = await self._run(
            "-i",
            str(csv_path),
            "-P",
            stack,
            "-A",
            f"{protocol}=annotations",
        )
        if code != 0:
            raise RuntimeError(f"sigrok decode failed: {stderr.strip() or stdout.strip()}")
        rows = [{"line": line} for line in stdout.splitlines() if line.strip()]
        return DecodeResult(protocol=protocol, rows=rows, annotations=stdout.splitlines(), source_capture=str(csv_path))

    def _build_decoder_stack(self, protocol: str, options: dict[str, str]) -> str:
        if protocol == "uart":
            rx = options.get("rx", "D0")
            return f"uart:rx={rx}"
        if protocol == "i2c":
            sda = options.get("sda", "D0")
            scl = options.get("scl", "D1")
            return f"i2c:sda={sda},scl={scl}"
        if protocol == "spi":
            clk = options.get("clk", "D0")
            mosi = options.get("mosi", "D1")
            miso = options.get("miso", "D2")
            return f"spi:clk={clk},mosi={mosi},miso={miso}"
        return protocol

    async def get_status(self) -> dict[str, Any]:
        return {
            "backend": self.name,
            "connected": self._device_id is not None,
            "device_id": self._device_id,
            "driver": self._driver,
            "cli": self._cli(),
            "cli_error": self._cli_error,
        }

    def _ensure_connected(self) -> None:
        if not self._device_id:
            raise RuntimeError("No sigrok device connected. Use la_device(operation='connect').")
