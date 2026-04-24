from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from llamacpp_panel.config import default_config_path, resolve_llama_server_path
from llamacpp_panel.gpu_enumeration import enumerate_gpus, nvidia_smi_executable
from llamacpp_panel.platform_util import apply_bundle_library_env, is_windows


def test_is_windows_matches_sys_platform() -> None:
    assert is_windows() == (sys.platform == "win32")


def test_resolve_llama_server_path_posix(tmp_path: Path) -> None:
    (tmp_path / "llama-server").write_bytes(b"")
    with patch("llamacpp_panel.config.is_windows", return_value=False):
        p = resolve_llama_server_path(str(tmp_path))
    assert p == tmp_path / "llama-server"


def test_resolve_llama_server_path_windows_prefers_exe(tmp_path: Path) -> None:
    (tmp_path / "llama-server.exe").write_bytes(b"")
    with patch("llamacpp_panel.config.is_windows", return_value=True):
        p = resolve_llama_server_path(str(tmp_path))
    assert p.name == "llama-server.exe"


def test_resolve_llama_server_path_windows_fallback_no_ext(tmp_path: Path) -> None:
    (tmp_path / "llama-server").write_bytes(b"")
    with patch("llamacpp_panel.config.is_windows", return_value=True):
        p = resolve_llama_server_path(str(tmp_path))
    assert p.name == "llama-server"


def test_apply_bundle_library_env_posix(tmp_path: Path) -> None:
    env: dict[str, str] = {}
    with patch("llamacpp_panel.platform_util.is_windows", return_value=False):
        apply_bundle_library_env(env, tmp_path)
    assert env.get("LD_LIBRARY_PATH") == str(tmp_path.resolve())


def test_apply_bundle_library_env_windows_prepends_path(tmp_path: Path) -> None:
    env = {"PATH": r"C:\Windows\System32"}
    with patch("llamacpp_panel.platform_util.is_windows", return_value=True):
        apply_bundle_library_env(env, tmp_path)
    assert env["PATH"].startswith(str(tmp_path.resolve()))
    assert "System32" in env["PATH"]


def test_default_config_path_uses_xdg_when_not_windows(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
    with patch("llamacpp_panel.config.is_windows", return_value=False):
        p = default_config_path()
    assert p == tmp_path / "llamacpp-panel" / "config.json"


def test_default_config_path_windows_uses_platformdirs(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    with patch("llamacpp_panel.config.is_windows", return_value=True):
        with patch("platformdirs.user_config_dir", return_value=r"C:\Users\me\AppData\Local\llamacpp-panel"):
            p = default_config_path()
    assert str(p).endswith("config.json")
    assert "llamacpp-panel" in str(p)


def test_nvidia_smi_executable_uses_which() -> None:
    with patch("llamacpp_panel.gpu_enumeration.shutil.which", side_effect=[None, r"C:\Program Files\...\nvidia-smi.exe"]):
        assert nvidia_smi_executable().endswith("nvidia-smi.exe")


def test_enumerate_gpus_invokes_resolved_nvidia_smi() -> None:
    captured: list[str] = []

    def fake_run(cmd: list[str], **kwargs: object) -> object:
        captured.append(cmd[0])
        class R:
            returncode = 0
            stdout = ""
            stderr = ""

        return R()

    with patch("llamacpp_panel.gpu_enumeration.subprocess.run", side_effect=fake_run):
        with patch("llamacpp_panel.gpu_enumeration.nvidia_smi_executable", return_value=r"C:\nv\nvidia-smi.exe"):
            enumerate_gpus()
    assert captured == [r"C:\nv\nvidia-smi.exe"]
