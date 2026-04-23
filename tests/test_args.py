from pathlib import Path

import pytest

from llamacpp_panel.args import build_llama_server_argv
from llamacpp_panel.config import LaunchProfile


def test_build_argv_local_minimal() -> None:
    fake = Path("/fake/llama-server")
    lp = LaunchProfile(
        model_mode="local",
        local_model_path="/models/m.gguf",
        server_host="127.0.0.1",
        server_port=8080,
        ctx_size=4096,
        n_gpu_layers=0,
        enable_metrics=False,
    )
    argv = build_llama_server_argv(fake, lp)
    assert argv[0] == str(fake)
    assert "-m" in argv
    assert "/models/m.gguf" in argv
    assert "--port" in argv
    assert "8080" in argv


def test_build_argv_hf() -> None:
    fake = Path("/fake/llama-server")
    lp = LaunchProfile(
        model_mode="hf",
        hf_repo="org/repo",
        server_host="0.0.0.0",
        server_port=9000,
        enable_metrics=True,
        api_key="secret",
    )
    argv = build_llama_server_argv(fake, lp)
    assert "-hf" in argv
    assert "org/repo" in argv
    assert "--metrics" in argv
    assert "--api-key" in argv
    assert "secret" in argv


def test_build_argv_rejects_empty_local() -> None:
    fake = Path("/fake/llama-server")
    lp = LaunchProfile(model_mode="local", local_model_path="")
    with pytest.raises(ValueError):
        build_llama_server_argv(fake, lp)
