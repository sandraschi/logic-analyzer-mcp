from __future__ import annotations

from logic_analyzer_mcp.config import BackendPreference, get_settings
from logic_analyzer_mcp.models.device import DeviceCapabilities, DeviceInfo
from logic_analyzer_mcp.services.backends.base import LogicAnalyzerBackend
from logic_analyzer_mcp.services.backends.sigrok import SigrokBackend
from logic_analyzer_mcp.services.backends.simulator import SimulatorBackend


class LogicSession:
    def __init__(self) -> None:
        self._backend: LogicAnalyzerBackend | None = None
        self._backend_name: str | None = None
        self._available = {
            "simulator": SimulatorBackend(),
            "sigrok": SigrokBackend(),
        }

    @property
    def backend(self) -> LogicAnalyzerBackend | None:
        return self._backend

    @property
    def backend_name(self) -> str | None:
        return self._backend_name

    def list_backend_names(self) -> list[str]:
        return list(self._available.keys())

    def get_backend(self, name: str) -> LogicAnalyzerBackend:
        backend = self._available.get(name)
        if backend is None:
            raise ValueError(f"Unknown backend '{name}'")
        return backend

    async def resolve_backend(self, preference: BackendPreference | None = None) -> LogicAnalyzerBackend:
        pref = preference or get_settings().backend
        if pref != "auto":
            backend = self.get_backend(pref)
            self._backend = backend
            self._backend_name = pref
            return backend
        for name in ("sigrok", "simulator"):
            backend = self.get_backend(name)
            try:
                devices = await backend.list_devices()
                if any(d.driver_status == "available" for d in devices):
                    self._backend = backend
                    self._backend_name = name
                    return backend
            except Exception:
                continue
        backend = self.get_backend("simulator")
        self._backend = backend
        self._backend_name = "simulator"
        return backend

    async def list_all_devices(self) -> list[DeviceInfo]:
        devices: list[DeviceInfo] = []
        for name in self.list_backend_names():
            backend = self.get_backend(name)
            try:
                devices.extend(await backend.list_devices())
            except Exception as exc:
                devices.append(
                    DeviceInfo(
                        device_id=f"{name}:unavailable",
                        backend="simulator",
                        model=f"{name} backend",
                        channel_labels=[],
                        connected=False,
                        capabilities=DeviceCapabilities(
                            backend="simulator",
                            channels=8,
                            max_sample_rate_hz=1_000_000,
                            notes=str(exc),
                        ),
                        driver_status="unavailable",
                        driver_hint=str(exc),
                    )
                )
        return devices

    async def connect(self, device_id: str, *, backend: str | None = None) -> DeviceInfo:
        if backend:
            selected = self.get_backend(backend)
        elif device_id.startswith("sigrok:"):
            selected = self.get_backend("sigrok")
        elif device_id.startswith("sim-"):
            selected = self.get_backend("simulator")
        else:
            prefix = device_id.split(":", maxsplit=1)[0]
            selected = self.get_backend(prefix) if prefix in self._available else await self.resolve_backend()
        if self._backend and self._backend is not selected:
            await self._backend.disconnect()
        self._backend = selected
        self._backend_name = selected.name
        return await selected.connect(device_id)

    async def disconnect(self) -> None:
        if self._backend is not None:
            await self._backend.disconnect()
        self._backend = None
        self._backend_name = None
