from __future__ import annotations

import asyncio
import os
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

from llamacpp_panel.args import build_llama_server_argv
from llamacpp_panel.config import AppConfig, LaunchProfile, resolve_llama_server_path
from llamacpp_panel.gpu_enumeration import apply_gpu_device_to_env
from llamacpp_panel.platform_util import apply_bundle_library_env, is_windows
from llamacpp_panel.logs import LogBroadcaster, RingBuffer


@dataclass
class SupervisedState:
    running: bool = False
    pid: int | None = None
    exit_code: int | None = None
    last_error: str | None = None


class LlamaSupervisor:
    def __init__(self, config_getter: Callable[[], AppConfig]) -> None:
        self._get_config = config_getter
        self.state = SupervisedState()
        self._proc: asyncio.subprocess.Process | None = None
        self._tasks: list[asyncio.Task[None]] = []
        self.buffer = RingBuffer(5000)
        self.broadcaster = LogBroadcaster()

    async def start(self, profile_override: LaunchProfile | None = None) -> None:
        if self._proc and self._proc.returncode is None:
            raise RuntimeError("llama-server is already running")

        cfg: AppConfig = self._get_config()
        profile = profile_override or cfg.launch_profile
        bin_dir = Path(cfg.llama_bin_dir).expanduser()
        server = resolve_llama_server_path(str(bin_dir))
        if not server.is_file():
            raise FileNotFoundError(f"llama-server not found at {server}")
        if not is_windows() and not os.access(server, os.X_OK):
            raise PermissionError(f"llama-server is not executable: {server}")

        try:
            argv = build_llama_server_argv(server, profile)
        except ValueError as e:
            self.state.last_error = str(e)
            raise

        env = os.environ.copy()
        apply_bundle_library_env(env, bin_dir.resolve())
        apply_gpu_device_to_env(env, profile.gpu_device_id)

        self.buffer = RingBuffer(cfg.log_buffer_lines)
        self.state = SupervisedState(running=True, last_error=None)
        try:
            self._proc = await asyncio.create_subprocess_exec(
                *argv,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                cwd=str(bin_dir.resolve()),
            )
        except Exception as e:
            self.state.running = False
            self.state.last_error = str(e)
            raise
        self.state.pid = self._proc.pid

        async def pump(
            stream: asyncio.StreamReader | None,
            prefix: str,
        ) -> None:
            if stream is None:
                return
            while True:
                line_b = await stream.readline()
                if not line_b:
                    break
                line = prefix + line_b.decode(errors="replace").rstrip()
                self.buffer.append(line)
                self.broadcaster.publish(line)

        assert self._proc.stdout and self._proc.stderr
        self._tasks = [
            asyncio.create_task(pump(self._proc.stdout, "")),
            asyncio.create_task(pump(self._proc.stderr, "[stderr] ")),
        ]

        asyncio.create_task(self._wait_exit())

    async def _wait_exit(self) -> None:
        if not self._proc:
            return
        code = await self._proc.wait()
        for t in self._tasks:
            t.cancel()
        self._tasks.clear()
        self.state.running = False
        self.state.exit_code = code
        self._proc = None
        msg = f"[supervisor] llama-server exited with code {code}"
        self.buffer.append(msg)
        self.broadcaster.publish(msg)

    async def stop(self) -> None:
        if not self._proc or self._proc.returncode is not None:
            self.state.running = False
            return
        self._proc.terminate()
        try:
            await asyncio.wait_for(self._proc.wait(), timeout=15.0)
        except TimeoutError:
            self._proc.kill()
            await self._proc.wait()
        self.state.running = False

    def snapshot_logs(self) -> list[str]:
        return self.buffer.snapshot()
