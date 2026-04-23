import os

from llamacpp_panel.gpu_enumeration import (
    apply_gpu_device_to_env,
    parse_nvidia_smi_csv,
)


def test_parse_nvidia_smi_csv() -> None:
    sample = """0, GPU-1111-2222-3333, NVIDIA GeForce RTX 4090
1, GPU-aaaa-bbbb-cccc, NVIDIA GeForce RTX 3060
"""
    devices = parse_nvidia_smi_csv(sample)
    assert len(devices) == 2
    assert devices[0].vendor == "NVIDIA"
    assert devices[0].id == "gpu:0"
    assert devices[0].uuid == "GPU-1111-2222-3333"
    assert "4090" in devices[0].name
    assert devices[1].id == "gpu:1"


def test_apply_gpu_prefix_sets_cuda_and_vulkan() -> None:
    env: dict[str, str] = {}
    apply_gpu_device_to_env(env, "gpu:1")
    assert env.get("CUDA_VISIBLE_DEVICES") == "1"
    assert env.get("GGML_VK_VISIBLE_DEVICES") == "1"


def test_apply_gpu_cuda_uuid_cuda_only() -> None:
    env: dict[str, str] = {}
    apply_gpu_device_to_env(env, "cuda:GPU-xyz")
    assert env.get("CUDA_VISIBLE_DEVICES") == "GPU-xyz"
    assert "GGML_VK_VISIBLE_DEVICES" not in env


def test_apply_cuda_numeric_sets_both() -> None:
    env: dict[str, str] = {}
    apply_gpu_device_to_env(env, "cuda:0")
    assert env.get("CUDA_VISIBLE_DEVICES") == "0"
    assert env.get("GGML_VK_VISIBLE_DEVICES") == "0"


def test_apply_gpu_vk_prefix() -> None:
    env: dict[str, str] = {}
    apply_gpu_device_to_env(env, "vk:1")
    assert env.get("GGML_VK_VISIBLE_DEVICES") == "1"
    assert "CUDA_VISIBLE_DEVICES" not in env


def test_apply_gpu_empty_noop() -> None:
    env = dict(os.environ)
    before_cuda = env.get("CUDA_VISIBLE_DEVICES")
    apply_gpu_device_to_env(env, "   ")
    assert env.get("CUDA_VISIBLE_DEVICES") == before_cuda
