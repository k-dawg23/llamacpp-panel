from __future__ import annotations

import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TypedDict

from llamacpp_panel.platform_util import is_windows


class ToolLaunchResult(TypedDict):
    ok: bool
    tool: str
    cwd: str
    message: str
    pid: int | None


def validate_project_folder(path_value: str) -> Path:
    folder = path_value.strip()
    if not folder:
        raise ValueError("selected project folder is empty")
    path = Path(folder).expanduser().resolve()
    if not path.exists():
        raise FileNotFoundError(f"project folder does not exist: {path}")
    if not path.is_dir():
        raise NotADirectoryError(f"project folder is not a directory: {path}")
    return path


def _terminal_command_for_pi(folder: Path, pi_executable: str) -> list[str]:
    if is_windows():
        cmd_exe = shutil.which("cmd.exe") or shutil.which("cmd")
        if not cmd_exe:
            raise FileNotFoundError("cmd.exe not found; cannot open pi in a terminal window")
        return [cmd_exe, "/k", pi_executable]

    pi_quoted = shlex.quote(pi_executable)
    folder_quoted = shlex.quote(str(folder))
    shell_command = f"cd {folder_quoted} && exec {pi_quoted}"

    terminal_candidates: list[list[str]] = [
        ["x-terminal-emulator", "-e", "bash", "-lc", shell_command],
        ["gnome-terminal", "--", "bash", "-lc", shell_command],
        ["konsole", "-e", "bash", "-lc", shell_command],
        ["kitty", "bash", "-lc", shell_command],
        ["alacritty", "-e", "bash", "-lc", shell_command],
        ["xterm", "-e", "bash", "-lc", shell_command],
    ]
    for candidate in terminal_candidates:
        resolved = shutil.which(candidate[0])
        if resolved:
            return [resolved, *candidate[1:]]

    if sys.platform == "darwin":
        osa = shutil.which("osascript")
        if osa:
            script = (
                'tell application "Terminal" to do script '
                f'"cd {folder_quoted} && exec {pi_quoted}"'
            )
            return [osa, "-e", script]

    raise FileNotFoundError("no supported terminal emulator found for launching pi")


def launch_pi_in_folder(path_value: str) -> ToolLaunchResult:
    folder = validate_project_folder(path_value)
    pi_executable = shutil.which("pi")
    if not pi_executable:
        raise FileNotFoundError("pi command not found on PATH")
    terminal_cmd = _terminal_command_for_pi(folder, pi_executable)

    popen_kwargs: dict[str, object] = {
        "cwd": str(folder),
        "close_fds": True,
        "env": os.environ.copy(),
    }
    if os.name == "nt":
        creationflags = getattr(subprocess, "CREATE_NEW_CONSOLE", 0)
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        popen_kwargs["creationflags"] = creationflags

    proc = subprocess.Popen(terminal_cmd, **popen_kwargs)
    return {
        "ok": True,
        "tool": "pi",
        "cwd": str(folder),
        "message": f"Opened pi in a terminal for {folder}",
        "pid": proc.pid,
    }
