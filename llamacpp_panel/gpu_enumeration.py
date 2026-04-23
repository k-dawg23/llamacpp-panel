from __future__ import annotations

import csv
import io
import subprocess
from typing import Literal

from pydantic import BaseModel


class GpuDevice(BaseModel):
    id: str
    name: str
    vendor: str


class GpuListResult(BaseModel):
    devices: list[GpuDevice]
    source: Literal["nvidia-smi", "none"]
    message: str = ""


def parse_nvidia_smi_csv(output: str) -> list[GpuDevice]:
    """Parse `nvidia-smi --query-gpu=index,uuid,name --format=csv,noheader` output."""
    devices: list[GpuDevice] = []
    reader = csv.reader(io.StringIO(output.strip()))
    for row in reader:
        if len(row) < 3:
            continue
        index, uuid, name = row[0].strip(), row[1].strip(), row[2].strip()
        if not name:
            continue
        stable = uuid if uuid else index
        dev_id = f"cuda:{stable}"
        devices.append(GpuDevice(id=dev_id, name=name, vendor="NVIDIA"))
    return devices


def enumerate_gpus() -> GpuListResult:
    try:
        proc = subprocess.run(
            [
                "nvidia-smi",
                "--query-gpu=index,uuid,name",
                "--format=csv,noheader",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except FileNotFoundError:
        return GpuListResult(
            devices=[],
            source="none",
            message="nvidia-smi not found on PATH",
        )
    except subprocess.TimeoutExpired:
        return GpuListResult(
            devices=[],
            source="none",
            message="nvidia-smi timed out",
        )

    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        return GpuListResult(
            devices=[],
            source="none",
            message=f"nvidia-smi failed ({proc.returncode}): {err[:200]}",
        )

    devices = parse_nvidia_smi_csv(proc.stdout or "")
    if not devices:
        return GpuListResult(
            devices=[],
            source="none",
            message="nvidia-smi returned no GPUs",
        )
    return GpuListResult(devices=devices, source="nvidia-smi", message="")


def apply_gpu_device_to_env(env: dict[str, str], gpu_device_id: str) -> None:
    """Restrict visible GPU(s) for the child process (CUDA or Vulkan per id prefix)."""
    raw = (gpu_device_id or "").strip()
    if not raw:
        return
    key_lower = raw.lower()
    if key_lower.startswith("vk:"):
        env["GGML_VK_VISIBLE_DEVICES"] = raw[3:].strip()
        return
    cuda_val = raw[5:].strip() if key_lower.startswith("cuda:") else raw
    if cuda_val:
        env["CUDA_VISIBLE_DEVICES"] = cuda_val
