from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal

import platformdirs
from pydantic import BaseModel, Field

from llamacpp_panel.platform_util import is_windows


def xdg_config_home() -> Path:
    env = os.environ.get("XDG_CONFIG_HOME", "").strip()
    if env:
        return Path(env).expanduser()
    return Path.home() / ".config"


def default_config_path() -> Path:
    if is_windows():
        base = Path(platformdirs.user_config_dir("llamacpp-panel", appauthor=False))
        return base / "config.json"
    return xdg_config_home() / "llamacpp-panel" / "config.json"


class LaunchProfile(BaseModel):
    model_mode: Literal["local", "hf"] = "local"
    local_model_path: str = ""
    hf_repo: str = ""
    server_host: str = "127.0.0.1"
    server_port: int = 8080
    ctx_size: int = 4096
    n_gpu_layers: int = 99
    enable_metrics: bool = False
    api_key: str = ""
    extra_args: str = ""
    gpu_device_id: str = ""


class AppConfig(BaseModel):
    llama_bin_dir: str = ""
    supervisor_host: str = "127.0.0.1"
    supervisor_port: int = 8742
    model_roots: list[str] = Field(default_factory=list)
    log_buffer_lines: int = 5000
    launch_profile: LaunchProfile = Field(default_factory=LaunchProfile)

    @classmethod
    def load(cls, path: Path | None = None) -> AppConfig:
        p = path or default_config_path()
        if not p.is_file():
            return cls()
        data = json.loads(p.read_text(encoding="utf-8"))
        return cls.model_validate(data)

    def save(self, path: Path | None = None) -> None:
        p = path or default_config_path()
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            json.dumps(self.model_dump(), indent=2) + "\n",
            encoding="utf-8",
        )


def resolve_llama_server_path(llama_bin_dir: str) -> Path:
    """Resolve the supervised executable inside ``llama_bin_dir``.

    On Windows, prefers ``llama-server.exe``, then a bare ``llama-server`` if present.
    On POSIX, uses ``llama-server``.
    """
    d = Path(llama_bin_dir).expanduser().resolve()
    if is_windows():
        exe = d / "llama-server.exe"
        if exe.is_file():
            return exe
        fallback = d / "llama-server"
        if fallback.is_file():
            return fallback
        return exe
    return d / "llama-server"
