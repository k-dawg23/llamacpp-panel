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

## Configuration

- **Bundle directory:** folder containing `llama-server` (for example an unpacked release). The supervisor prepends this directory to `LD_LIBRARY_PATH` for the child process only.
- **Model roots:** directories scanned for `.gguf` files.
- **Launch profile:** `llama-server` flags such as context size, GPU layers, metrics, API key, local path (`-m`) or Hugging Face repo (`-hf`).

Hugging Face downloads use the standard cache via `huggingface_hub` (login with `huggingface-cli login` if a repo is gated).

## Multi-GPU (NVIDIA)

The panel can list NVIDIA GPUs via `nvidia-smi` and save a **GPU device** on the launch profile. When you start `llama-server`, the supervisor sets:

- **`CUDA_VISIBLE_DEVICES`** for IDs returned from detection (stored as `cuda:…`, for example `cuda:GPU-uuid` or `cuda:0` after normalization).
- **`GGML_VK_VISIBLE_DEVICES`** only if you enter an id of the form **`vk:N`** (manual Vulkan device index). Vulkan builds do not yet get automatic enumeration here.

If `nvidia-smi` is missing (typical for Vulkan-only or CPU machines), the list is empty and inference still works as before; you can leave the device as **Default** or set a manual `vk:` id for Vulkan.

## Tests

```bash
source .venv/bin/activate
pytest
```

## License

MIT — see [LICENSE](LICENSE).

## Git

This repository is intended to be used with Git for version control (`git init` / clone as usual).
