# llamacpp-panel

Local web UI and supervisor for [llama.cpp](https://github.com/ggml-org/llama.cpp) `llama-server` on Linux (tested layout: Ubuntu 24.04, Vulkan tarball bundles).

## Prerequisites

- **Python** 3.11+
- **Node.js** 20+ (only to build the web UI)
- A working **llama.cpp** build or release bundle containing `llama-server` (and typically sibling `.so` files for portable Vulkan builds)

Optional: Vulkan drivers for GPU inference when using a Vulkan build.

## Setup

```bash
cd /path/to/llama_front_end
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd web && npm install && npm run build && cd ..
```

## Run

**Production-style (API + built UI on one port):**

```bash
source .venv/bin/activate
python -m llamacpp_panel
```

Open `http://127.0.0.1:8742` (configurable via `~/.config/llamacpp-panel/config.json`).

**Development (hot reload UI, API proxied):**

Terminal 1:

```bash
source .venv/bin/activate
uvicorn llamacpp_panel.app:app --host 127.0.0.1 --port 8742 --reload
```

Terminal 2:

```bash
cd web && npm run dev
```

Open `http://127.0.0.1:5173` — Vite proxies `/api` to port 8742.

## User guide

In-app **Help** tab (after `npm run build`) mirrors [`docs/panel-user-guide.md`](docs/panel-user-guide.md): every tab, field, and primary action explained.

## Configuration

- **Bundle directory:** folder containing `llama-server` (for example an unpacked release). The supervisor prepends this directory to `LD_LIBRARY_PATH` for the child process only.
- **Model roots:** directories scanned for `.gguf` files.
- **Launch profile:** `llama-server` flags such as context size, GPU layers, metrics, API key, local path (`-m`) or Hugging Face repo (`-hf`).

Hugging Face downloads use the standard cache via `huggingface_hub` (login with `huggingface-cli login` if a repo is gated).

## Multi-GPU (NVIDIA)

The panel lists NVIDIA GPUs via `nvidia-smi` using each card’s **driver index** (`gpu:0`, `gpu:1`, …). When you start `llama-server`, the supervisor sets:

- **`CUDA_VISIBLE_DEVICES`** to that index (or UUID) for CUDA builds.
- **`GGML_VK_VISIBLE_DEVICES`** to the **same index** when the saved value is numeric (covers typical **Vulkan** tarballs on multi‑GPU NVIDIA boxes). Vulkan and CUDA device order usually match for discrete GPUs; if not, set a manual **`vk:N`** id (Vulkan only) after checking `vulkaninfo` / `llama-server --list-devices` for your build.

Older configs may still store `cuda:GPU-…` (UUID); that affects CUDA only—**re-pick the GPU** in Settings so the profile uses `gpu:N` and Vulkan sees a single device.

If `nvidia-smi` is missing, use **Default** or a manual **`vk:N`** line in the GPU field.

## Tests

```bash
source .venv/bin/activate
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Git

This repository is intended to be used with Git for version control (`git init` / clone as usual).
