from __future__ import annotations

import csv
import io
import shutil
import subprocess
from typing import Literal

from pydantic import BaseModel


class GpuDevice(BaseModel):
    """id uses `gpu:{index}` from nvidia-smi so one pick maps to CUDA and Vulkan."""

    id: str
    name: str
    vendor: str
    uuid: str = ""


class GpuListResult(BaseModel):
    devices: list[GpuDevice]
    source: Literal["nvidia-smi", "none"]
    message: str = ""


def nvidia_smi_executable() -> str:
    """Return ``nvidia-smi`` on PATH, trying ``.exe`` on Windows via :func:`shutil.which`."""
    for name in ("nvidia-smi", "nvidia-smi.exe"):
        p = shutil.which(name)
        if p:
            return p
    return "nvidia-smi"


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
        dev_id = f"gpu:{index}"
        devices.append(GpuDevice(id=dev_id, name=name, vendor="NVIDIA", uuid=uuid))
    return devices


def enumerate_gpus() -> GpuListResult:
    try:
        proc = subprocess.run(
            [
                nvidia_smi_executable(),
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
    """Restrict visible GPU(s) for the child process.

    - ``vk:N`` → ``GGML_VK_VISIBLE_DEVICES`` only (Vulkan builds).
    - ``gpu:N`` from our enumerator → ``CUDA_VISIBLE_DEVICES`` and ``GGML_VK_VISIBLE_DEVICES``
      (NVIDIA index usually matches Vulkan device order for discrete GPUs; use ``vk:`` if not).
    - ``cuda:…`` → ``CUDA_VISIBLE_DEVICES``; if the value is a plain integer, also set Vulkan
      (legacy); UUID-only selections affect CUDA only.
    """
    raw = (gpu_device_id or "").strip()
    if not raw:
        return
    lk = raw.lower()
    if lk.startswith("vk:"):
        env["GGML_VK_VISIBLE_DEVICES"] = raw[3:].strip()
        return
    val: str
    if lk.startswith("gpu:"):
        val = raw[4:].strip()
    elif lk.startswith("cuda:"):
        val = raw[5:].strip()
    else:
        val = raw
    if not val:
        return
    env["CUDA_VISIBLE_DEVICES"] = val
    if val.isdigit():
        env["GGML_VK_VISIBLE_DEVICES"] = val
