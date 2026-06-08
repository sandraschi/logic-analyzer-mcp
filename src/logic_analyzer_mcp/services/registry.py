from __future__ import annotations

from logic_analyzer_mcp.models.capture import DecodeResult, LogicCapture
from logic_analyzer_mcp.services.backends.base import LogicAnalyzerBackend
from logic_analyzer_mcp.services.session import LogicSession

_session: LogicSession | None = None
_last_capture: LogicCapture | None = None
_last_decode: DecodeResult | None = None


def get_session() -> LogicSession:
    global _session
    if _session is None:
        _session = LogicSession()
    return _session


def set_last_capture(capture: LogicCapture) -> None:
    global _last_capture
    _last_capture = capture


def get_last_capture() -> LogicCapture | None:
    return _last_capture


def set_last_decode(result: DecodeResult) -> None:
    global _last_decode
    _last_decode = result


def get_last_decode() -> DecodeResult | None:
    return _last_decode


def get_active_backend() -> LogicAnalyzerBackend | None:
    return get_session().backend


async def clear_services() -> None:
    global _session, _last_capture, _last_decode
    if _session is not None:
        await _session.disconnect()
    _session = None
    _last_capture = None
    _last_decode = None
