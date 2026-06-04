from __future__ import annotations

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from llamacpp_panel.app import create_app, state
from llamacpp_panel.config import AppConfig
from llamacpp_panel.tool_launchers import (
    _terminal_command_for_pi,
    launch_pi_in_folder,
    validate_project_folder,
)


def test_validate_project_folder_rejects_empty() -> None:
    with pytest.raises(ValueError, match="selected project folder is empty"):
        validate_project_folder("")


def test_validate_project_folder_rejects_missing(tmp_path: Path) -> None:
    missing = tmp_path / "missing"
    with pytest.raises(FileNotFoundError, match="project folder does not exist"):
        validate_project_folder(str(missing))


def test_validate_project_folder_rejects_file(tmp_path: Path) -> None:
    file_path = tmp_path / "file.txt"
    file_path.write_text("x", encoding="utf-8")
    with pytest.raises(NotADirectoryError, match="project folder is not a directory"):
        validate_project_folder(str(file_path))


def test_terminal_command_for_pi_prefers_terminal_emulator(tmp_path: Path) -> None:
    with patch("llamacpp_panel.tool_launchers.is_windows", return_value=False):
        with patch(
            "llamacpp_panel.tool_launchers.shutil.which",
            side_effect=lambda name: "/usr/bin/x-terminal-emulator" if name == "x-terminal-emulator" else None,
        ):
            cmd = _terminal_command_for_pi(tmp_path, "/usr/bin/pi")

    assert cmd[:4] == ["/usr/bin/x-terminal-emulator", "-e", "bash", "-lc"]
    assert "exec /usr/bin/pi" in cmd[4]


def test_terminal_command_for_pi_requires_supported_terminal(tmp_path: Path) -> None:
    with patch("llamacpp_panel.tool_launchers.is_windows", return_value=False):
        with patch("llamacpp_panel.tool_launchers.shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="no supported terminal emulator found"):
                _terminal_command_for_pi(tmp_path, "/usr/bin/pi")


def test_launch_pi_in_folder_opens_terminal_with_resolved_cwd(tmp_path: Path) -> None:
    captured: dict[str, object] = {}

    class DummyProc:
        pid = 4321

    def fake_popen(cmd: list[str], **kwargs: object) -> DummyProc:
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return DummyProc()

    with patch("llamacpp_panel.tool_launchers.shutil.which", return_value="/usr/bin/pi"):
        with patch(
            "llamacpp_panel.tool_launchers._terminal_command_for_pi",
            return_value=["/usr/bin/x-terminal-emulator", "-e", "bash", "-lc", "exec /usr/bin/pi"],
        ):
            with patch("llamacpp_panel.tool_launchers.subprocess.Popen", side_effect=fake_popen):
                result = launch_pi_in_folder(str(tmp_path))

    assert result["ok"] is True
    assert result["cwd"] == str(tmp_path.resolve())
    assert result["pid"] == 4321
    assert result["message"] == f"Opened pi in a terminal for {tmp_path.resolve()}"
    assert captured["cmd"] == ["/usr/bin/x-terminal-emulator", "-e", "bash", "-lc", "exec /usr/bin/pi"]
    assert captured["kwargs"]["cwd"] == str(tmp_path.resolve())


def test_terminal_command_for_pi_uses_cmd_on_windows(tmp_path: Path) -> None:
    with patch("llamacpp_panel.tool_launchers.is_windows", return_value=True):
        with patch(
            "llamacpp_panel.tool_launchers.shutil.which",
            side_effect=lambda name: r"C:\Windows\System32\cmd.exe" if name in {"cmd.exe", "cmd"} else None,
        ):
            cmd = _terminal_command_for_pi(tmp_path, r"C:\tools\pi.exe")

    assert cmd == [r"C:\Windows\System32\cmd.exe", "/k", r"C:\tools\pi.exe"]


def test_terminal_command_for_pi_requires_cmd_on_windows(tmp_path: Path) -> None:
    with patch("llamacpp_panel.tool_launchers.is_windows", return_value=True):
        with patch("llamacpp_panel.tool_launchers.shutil.which", return_value=None):
            with pytest.raises(FileNotFoundError, match="cmd.exe not found"):
                _terminal_command_for_pi(tmp_path, r"C:\tools\pi.exe")


def test_launch_pi_in_folder_requires_pi_on_path(tmp_path: Path) -> None:
    with patch("llamacpp_panel.tool_launchers.shutil.which", return_value=None):
        with pytest.raises(FileNotFoundError, match="pi command not found on PATH"):
            launch_pi_in_folder(str(tmp_path))


def test_pi_start_endpoint_uses_selected_folder(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    original_config = state.config
    try:
        state.config = AppConfig(selected_project_folder=str(tmp_path))
        with patch("llamacpp_panel.app.launch_pi_in_folder") as launch_mock:
            launch_mock.return_value = {
                "ok": True,
                "tool": "pi",
                "cwd": str(tmp_path),
                "message": "Opened pi in a terminal",
                "pid": 77,
            }
            response = client.post("/api/tools/pi/start", json={})
    finally:
        state.config = original_config

    assert response.status_code == 200
    assert response.json()["cwd"] == str(tmp_path)
    launch_mock.assert_called_once_with(str(tmp_path))


def test_pi_start_endpoint_returns_validation_error(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    original_config = state.config
    try:
        state.config = AppConfig()
        response = client.post("/api/tools/pi/start", json={"project_folder": ""})
    finally:
        state.config = original_config

    assert response.status_code == 400
    assert response.json()["detail"] == "selected project folder is empty"


def test_pi_start_endpoint_surfaces_spawn_error(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    original_config = state.config
    try:
        state.config = AppConfig(selected_project_folder=str(tmp_path))
        with patch(
            "llamacpp_panel.app.launch_pi_in_folder",
            side_effect=subprocess.SubprocessError("spawn failed"),
        ):
            response = client.post("/api/tools/pi/start", json={})
    finally:
        state.config = original_config

    assert response.status_code == 400
    assert response.json()["detail"] == "spawn failed"


def test_pick_directory_endpoint_returns_selected_path(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    with patch("llamacpp_panel.app.pick_directory", return_value=str(tmp_path)) as picker_mock:
        response = client.post(
            "/api/dialogs/pick-directory",
            json={"title": "Choose folder", "initial_dir": str(tmp_path)},
        )

    assert response.status_code == 200
    assert response.json() == {"path": str(tmp_path)}
    picker_mock.assert_called_once_with(title="Choose folder", initial_dir=str(tmp_path))


def test_pick_directory_endpoint_returns_null_on_cancel(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    with patch("llamacpp_panel.app.pick_directory", return_value=None):
        response = client.post(
            "/api/dialogs/pick-directory",
            json={"title": "Choose folder"},
        )

    assert response.status_code == 200
    assert response.json() == {"path": None}


def test_pick_directory_endpoint_surfaces_picker_error(tmp_path: Path) -> None:
    app = create_app(web_dist=tmp_path / "missing-dist")
    client = TestClient(app)
    with patch("llamacpp_panel.app.pick_directory", side_effect=RuntimeError("dialog unavailable")):
        response = client.post(
            "/api/dialogs/pick-directory",
            json={"title": "Choose folder"},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "dialog unavailable"
