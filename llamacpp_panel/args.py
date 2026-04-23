from __future__ import annotations

import shlex
from pathlib import Path

from llamacpp_panel.config import LaunchProfile


def build_llama_server_argv(
    llama_server: Path,
    profile: LaunchProfile,
) -> list[str]:
    """Build argument list for llama-server from profile (excluding argv[0])."""
    args: list[str] = [str(llama_server)]

    if profile.model_mode == "hf":
        repo = profile.hf_repo.strip()
        if not repo:
            raise ValueError("Hugging Face repo is required when model_mode is hf")
        args.extend(["-hf", repo])
    else:
        path = profile.local_model_path.strip()
        if not path:
            raise ValueError("Local model path is required when model_mode is local")
        args.extend(["-m", path])

    args.extend(["--host", profile.server_host.strip() or "127.0.0.1"])
    args.extend(["--port", str(profile.server_port)])

    if profile.ctx_size > 0:
        args.extend(["-c", str(profile.ctx_size)])

    if profile.n_gpu_layers >= 0:
        args.extend(["-ngl", str(profile.n_gpu_layers)])

    if profile.enable_metrics:
        args.append("--metrics")

    key = profile.api_key.strip()
    if key:
        args.extend(["--api-key", key])

    extra = profile.extra_args.strip()
    if extra:
        args.extend(shlex.split(extra))

    return args
