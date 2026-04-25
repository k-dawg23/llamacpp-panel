# llamacpp-panel

Local web UI and supervisor for [llama.cpp](https://github.com/ggml-org/llama.cpp) `llama-server`. **Linux** (tested: Ubuntu 24.04, Vulkan tarball bundles) and **Windows 10 / 11** (native Python; single-user, localhost-first; **manual smoke: Windows 11 only**—Windows 10 is expected to match but not separately tested).

## Prerequisites

- **Python** 3.11+
- **Node.js** 20+ (only to build the web UI)
- A working **llama.cpp** build or release bundle:
  - **Linux:** `llama-server` plus sibling `.so` files when using portable bundles.
  - **Windows:** `llama-server.exe` plus sibling `.dll` files in the same folder (typical release layout).

Optional: Vulkan or CUDA drivers for GPU inference, depending on your `llama-server` build.

**Python command:** On **Linux**, use `python3` (or `python` if that points to 3.11+). On **Windows**, the [Python launcher](https://docs.python.org/3/using/windows.html#python-launcher-for-windows) `py` is recommended, e.g. `py -3.11`.

**Chaining commands:** In **bash/zsh**, `a && b` runs `b` only if `a` succeeds. **Windows PowerShell 5.x** (default in older setups) does **not** support `&&`; use **`;`** instead (e.g. `cd web; npm install; npm run build; cd ..`). **PowerShell 7+** adds `&&`—if yours supports it, you can use either style.

## Setup

**Linux / macOS (bash or zsh)** — use `source` to activate; do **not** use this in PowerShell.

```bash
cd /path/to/llama_front_end
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cd web && npm install && npm run build && cd ..
```

**Windows (PowerShell in VS Code or similar)** — `source` is not valid; activate with the script under `Scripts`:

```powershell
cd C:\path\to\llama_front_end
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If execution policy blocks activation, run once: `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` (or use **Command Prompt** and `.\.venv\Scripts\activate.bat`).

```powershell
pip install -e ".[dev]"
cd web; npm install; npm run build; cd ..
```

## Run

**Production-style (API + built UI on one port):**

Linux / macOS:

```bash
source .venv/bin/activate
python3 -m llamacpp_panel
```

Windows (venv activated as above):

```powershell
py -m llamacpp_panel
```

Open `http://127.0.0.1:8742`. **Config file location:**

- **Linux / other POSIX:** `~/.config/llamacpp-panel/config.json` (or `$XDG_CONFIG_HOME/llamacpp-panel/config.json`).
- **Windows:** `%LOCALAPPDATA%\llamacpp-panel\config.json` (via [platformdirs](https://pypi.org/project/platformdirs/)).

**Development (hot reload UI, API proxied):**

Terminal 1 — Linux / macOS:

```bash
source .venv/bin/activate
uvicorn llamacpp_panel.app:app --host 127.0.0.1 --port 8742 --reload
```

Terminal 1 — Windows (PowerShell, venv activated):

```powershell
py -m uvicorn llamacpp_panel.app:app --host 127.0.0.1 --port 8742 --reload
```

Terminal 2 — Linux / macOS:

```bash
cd web && npm run dev
```

Terminal 2 — Windows (PowerShell):

```powershell
cd web; npm run dev
```

Open `http://127.0.0.1:5173` — Vite proxies `/api` to port 8742.

## User guide

In-app **Help** tab (after `npm run build`) mirrors [`docs/panel-user-guide.md`](docs/panel-user-guide.md): every tab, field, and primary action explained.

## Configuration

- **Bundle directory:** folder containing `llama-server` (Linux) or `llama-server.exe` (Windows). For the supervised child only, the panel prepends this directory to **`LD_LIBRARY_PATH`** on POSIX or to **`PATH`** on Windows so bundled shared libraries resolve (same idea as the Linux tarball layout; Windows uses DLL load rules).

- **Model roots:** directories scanned for `.gguf` files.
- **Launch profile:** `llama-server` flags such as context size, GPU layers, metrics, API key, local path (`-m`) or Hugging Face repo (`-hf`).

Hugging Face downloads use `huggingface_hub` with the **exact file name** from the repo’s **Files** list—not the `llama-server -hf org/repo:quant` shorthand (the part after `:` is llama.cpp-specific). Example: for `llama-server -hf unsloth/Qwen3.5-4B-GGUF:UD-Q4_K_XL`, the panel wants repo **`unsloth/Qwen3.5-4B-GGUF`** and filename **`Qwen3.5-4B-UD-Q4_K_XL.gguf`**. For gated repos, run `huggingface-cli login` (or set `HF_TOKEN`). On Windows you can use `py -m huggingface_hub.cli.huggingface_cli login` if `huggingface-cli` is not on PATH.

### Windows notes

- Use a **native Windows** `llama-server.exe` with **native Windows Python** (not WSL-only binaries unless you run the whole stack in WSL).
- If `llama-server` exits immediately and Event Viewer faults **`MSVCP140.dll`** (or `VCRUNTIME*.dll`), install the **Microsoft Visual C++ Redistributable (x64)**—you do not need the full Visual Studio IDE.
- **Stop** uses Python’s process API; graceful shutdown is weaker than POSIX `SIGTERM`—expect best-effort termination.
- **GPU list:** `nvidia-smi` / `nvidia-smi.exe` on `PATH` uses the same CSV query as on Linux.

## Multi-GPU (NVIDIA)

The panel lists NVIDIA GPUs via `nvidia-smi` using each card’s **driver index** (`gpu:0`, `gpu:1`, …). When you start `llama-server`, the supervisor sets:

- **`CUDA_VISIBLE_DEVICES`** to that index (or UUID) for CUDA builds.
- **`GGML_VK_VISIBLE_DEVICES`** to the **same index** when the saved value is numeric (covers typical **Vulkan** tarballs on multi‑GPU NVIDIA boxes). Vulkan and CUDA device order usually match for discrete GPUs; if not, set a manual **`vk:N`** id (Vulkan only) after checking `vulkaninfo` / `llama-server --list-devices` for your build.

Older configs may still store `cuda:GPU-…` (UUID); that affects CUDA only—**re-pick the GPU** in Settings so the profile uses `gpu:N` and Vulkan sees a single device.

If `nvidia-smi` is missing, use **Default** or a manual **`vk:N`** line in the GPU field.

## Tests

```bash
source .venv/bin/activate
python3 -m pytest
```

Windows (PowerShell, venv activated): `py -m pytest`.

## License

MIT — see [LICENSE](LICENSE).

## Git

This repository is intended to be used with Git for version control (`git init` / clone as usual).
