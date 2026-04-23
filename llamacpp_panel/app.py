from __future__ import annotations

import asyncio
import json
import os
import subprocess
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from llamacpp_panel.config import (
    AppConfig,
    LaunchProfile,
    default_config_path,
    resolve_llama_server_path,
)
from llamacpp_panel.hf_download import HfJobManager
from llamacpp_panel.logs import RingBuffer
from llamacpp_panel.models_scan import scan_gguf_roots
from llamacpp_panel.monitoring import fetch_llama_server_status
from llamacpp_panel.supervisor import LlamaSupervisor


class ConfigUpdatePayload(BaseModel):
    llama_bin_dir: str | None = None
    supervisor_host: str | None = None
    supervisor_port: int | None = None
    model_roots: list[str] | None = None
    log_buffer_lines: int | None = None
    launch_profile: dict[str, Any] | None = None


class ValidateBinaryPayload(BaseModel):
    llama_bin_dir: str | None = None


class SupervisorStartPayload(BaseModel):
    launch_profile: dict[str, Any] | None = None


class HfDownloadPayload(BaseModel):
    repo_id: str = Field(..., min_length=1)
    filename: str = Field(..., min_length=1)


class AppState:
    def __init__(self) -> None:
        self.config_path = default_config_path()
        self.config = AppConfig.load(self.config_path)
        self.supervisor = LlamaSupervisor(lambda: self.config)
        self.hf_jobs = HfJobManager()


state = AppState()


def create_app(
    web_dist: Path | None = None,
) -> FastAPI:
    app = FastAPI(title="llamacpp-panel")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    dist = web_dist
    if dist is None:
        dist = Path(__file__).resolve().parent / "static" / "web"

    @app.get("/api/config")
    async def get_config() -> dict[str, Any]:
        return state.config.model_dump()

    @app.put("/api/config")
    async def put_config(payload: ConfigUpdatePayload) -> dict[str, Any]:
        data = state.config.model_dump()
        patch = payload.model_dump(exclude_none=True)
        if "launch_profile" in patch and patch["launch_profile"] is not None:
            data["launch_profile"] = {**data["launch_profile"], **patch["launch_profile"]}
            del patch["launch_profile"]
        data.update(patch)
        state.config = AppConfig.model_validate(data)
        state.config.save(state.config_path)
        state.supervisor.buffer = RingBuffer(state.config.log_buffer_lines)
        return state.config.model_dump()

    @app.post("/api/validate-binary")
    async def validate_binary(payload: ValidateBinaryPayload) -> dict[str, Any]:
        d = (payload.llama_bin_dir or state.config.llama_bin_dir or "").strip()
        if not d:
            return {"ok": False, "error": "llama_bin_dir is empty"}
        server = resolve_llama_server_path(d)
        if not server.is_file():
            return {
                "ok": False,
                "server_path": str(server),
                "error": "llama-server not found",
            }
        if not os.access(server, os.X_OK):
            return {
                "ok": False,
                "server_path": str(server),
                "error": "llama-server is not executable",
            }
        version_out = ""
        try:
            bin_dir = Path(d).expanduser().resolve()
            env = os.environ.copy()
            env["LD_LIBRARY_PATH"] = (
                f"{bin_dir}:{env['LD_LIBRARY_PATH']}" if env.get("LD_LIBRARY_PATH") else str(bin_dir)
            )
            proc = subprocess.run(
                [str(server), "--version"],
                capture_output=True,
                text=True,
                timeout=15,
                env=env,
                cwd=str(bin_dir),
            )
            version_out = (proc.stdout or proc.stderr or "").strip()
        except Exception as e:
            version_out = f"(could not run --version: {e})"
        return {
            "ok": True,
            "server_path": str(server),
            "version_output": version_out,
        }

    @app.get("/api/supervisor/status")
    async def supervisor_status() -> dict[str, Any]:
        s = state.supervisor.state
        return {
            "running": s.running,
            "pid": s.pid,
            "exit_code": s.exit_code,
            "last_error": s.last_error,
        }

    @app.post("/api/supervisor/start")
    async def supervisor_start(
        payload: SupervisorStartPayload | None = None,
    ) -> dict[str, Any]:
        profile_override: LaunchProfile | None = None
        if payload and payload.launch_profile:
            merged = {**state.config.launch_profile.model_dump(), **payload.launch_profile}
            profile_override = LaunchProfile.model_validate(merged)
        try:
            await state.supervisor.start(profile_override)
        except Exception as e:
            state.supervisor.state.last_error = str(e)
            raise HTTPException(status_code=400, detail=str(e)) from e
        return await supervisor_status()

    @app.post("/api/supervisor/stop")
    async def supervisor_stop() -> dict[str, Any]:
        await state.supervisor.stop()
        return await supervisor_status()

    @app.get("/api/logs")
    async def get_logs() -> dict[str, Any]:
        return {"lines": state.supervisor.snapshot_logs()}

    @app.get("/api/logs/stream")
    async def logs_stream(request: Request) -> StreamingResponse:
        async def gen():
            q = state.supervisor.broadcaster.subscribe()
            try:
                for line in state.supervisor.snapshot_logs():
                    if await request.is_disconnected():
                        return
                    yield f"data: {json.dumps({'line': line})}\n\n"
                while True:
                    if await request.is_disconnected():
                        return
                    try:
                        line = await asyncio.wait_for(q.get(), timeout=30.0)
                        yield f"data: {json.dumps({'line': line})}\n\n"
                    except TimeoutError:
                        yield ": keepalive\n\n"
            finally:
                state.supervisor.broadcaster.unsubscribe(q)

        return StreamingResponse(
            gen(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    @app.get("/api/models/local")
    async def models_local() -> dict[str, Any]:
        entries = await scan_gguf_roots(state.config.model_roots)
        return {"models": [e.model_dump() for e in entries]}

    @app.post("/api/hf/download")
    async def hf_download(payload: HfDownloadPayload) -> dict[str, Any]:
        job = state.hf_jobs.start_download(payload.repo_id.strip(), payload.filename.strip())
        return {"job_id": job.id}

    @app.get("/api/hf/jobs/{job_id}")
    async def hf_job(job_id: str) -> dict[str, Any]:
        job = state.hf_jobs.get(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="job not found")
        return {
            "id": job.id,
            "repo_id": job.repo_id,
            "filename": job.filename,
            "status": job.status,
            "progress": job.progress,
            "error": job.error,
            "local_path": job.local_path,
        }

    @app.get("/api/monitor")
    async def monitor() -> dict[str, Any]:
        lp = state.config.launch_profile
        base = f"http://{lp.server_host}:{lp.server_port}"
        key = lp.api_key.strip() or None
        return await fetch_llama_server_status(base, api_key=key)

    if dist.is_dir():
        app.mount(
            "/assets",
            StaticFiles(directory=str(dist / "assets")),
            name="assets",
        )

        @app.get("/{full_path:path}")
        async def spa_fallback(full_path: str) -> FileResponse:
            target = dist / full_path
            if target.is_file():
                return FileResponse(target)
            return FileResponse(dist / "index.html")

    return app


app = create_app()
