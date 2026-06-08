from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BackendPreference = Literal["auto", "simulator", "sigrok"]


def _load_dotenv_files() -> None:
    for candidate in (Path.cwd() / ".env", Path(__file__).resolve().parents[2] / ".env"):
        if candidate.exists():
            load_dotenv(candidate)
            return


class LogicAnalyzerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LOGIC_ANALYZER_MCP_", extra="ignore")

    backend: BackendPreference = "auto"
    device_id: str | None = None
    capture_dir: Path = Path("./captures")
    sigrok_cli: str = "sigrok-cli"
    transport: Literal["stdio", "http", "sse"] = "stdio"
    host: str = "127.0.0.1"
    port: int = 10985
    webapp_port: int = 10987
    path: str = "/mcp"
    log_level: str = "INFO"

    @field_validator("capture_dir", mode="before")
    @classmethod
    def expand_capture_dir(cls, value: str | Path) -> Path:
        return Path(value).expanduser()

    @field_validator("port", "webapp_port")
    @classmethod
    def validate_port(cls, value: int) -> int:
        return max(1024, min(65535, value))


@lru_cache(maxsize=1)
def get_settings() -> LogicAnalyzerSettings:
    _load_dotenv_files()
    if os.getenv("LOGIC_ANALYZER_ALLOW_LOGGING", "").lower() in ("1", "true", "yes"):
        pass
    return LogicAnalyzerSettings()
