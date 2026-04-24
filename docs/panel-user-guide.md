# llamacpp-panel user guide

This document describes the **llamacpp-panel** web UI: what each tab does, what to enter in Settings, and how it maps to [llama.cpp](https://github.com/ggml-org/llama.cpp) `llama-server`. For install and CLI usage, see the repository [README](../README.md).

---

## Windows (10 / 11)

- **Bundle directory:** use the folder that contains **`llama-server.exe`** and the usual **`.dll`** dependencies next to it (same pattern as Linux `.so` siblings).
- **Library search:** the supervisor prepends the bundle directory to the child’s **`PATH`** (not `LD_LIBRARY_PATH`, which Windows ignores for native executables).
- **Config file:** `%LOCALAPPDATA%\llamacpp-panel\config.json` (not `~/.config` on Windows).
- **Validate binary** does not require POSIX “execute bits”; it checks the file exists (and runs `--version` when possible).
- **Stop server:** termination is **best-effort** compared to Linux (no full SIGTERM semantics).
- **GPUs:** if **`nvidia-smi`** or **`nvidia-smi.exe`** is on `PATH`, the Settings GPU list works like on Linux.
- Run **native Windows Python** with a **Windows** `llama-server` build; mixing WSL binaries with a Windows-hosted panel is unsupported.
- **PowerShell:** use **`;`** to chain commands (e.g. `cd web; npm run build`), not **`&&`** (that is bash; only PowerShell 7+ supports `&&`).

---

## Tabs overview

| Tab | Purpose |
|-----|---------|
| **Settings** | Binary path, model scan roots, launch profile (`llama-server` arguments), GPU pick, presets. |
| **Models** | Scan local `.gguf` files, set the active model with **Use**, Hugging Face downloads. |
| **Server** | Start/stop the supervised `llama-server` and view streamed logs. |
| **Monitor** | Poll the running server’s HTTP health/props/slots/metrics (if enabled). |
| **Help** | This guide rendered inside the app. |

---

## Settings

### Paths and supervisor

- **llama.cpp bundle directory**  
  Absolute path to the folder containing the `llama-server` executable (Linux) or `llama-server.exe` (Windows), with sibling shared libraries (`.so` / `.dll`) for portable bundles.  
  **Save path** writes it to config. **Validate binary** checks that the executable exists (POSIX: executable bit; Windows: file present + `--version` probe).

- **Model roots (one per line)**  
  Directories searched when you click **Scan GGUF** on the Models tab. Paths should be absolute or as you use on the host. **Save model roots** persists the list.

### Launch profile

These values are passed (with small transformations) when the supervisor starts `llama-server`. Exact flags depend on your binary; run `llama-server --help` for the authoritative list.

| Field | Meaning | Typical values |
|-------|---------|----------------|
| **Model mode** | `local` uses `-m` with a file path; `hf` uses Hugging Face repo mode (`-hf`) when your build supports it. | `local` / `hf` |
| **Server host** | HTTP bind for `llama-server` (e.g. `127.0.0.1`). | `127.0.0.1` or `0.0.0.0` (wider exposure) |
| **Server port** | HTTP port. | `8080`, `11434`, etc. |
| **Context (-c)** | Context size in tokens. Must fit model + VRAM/RAM. | `4096`–`131072` depending on model |
| **GPU layers (-ngl)** | Layers offloaded to GPU (`99` often means “all” in llama.cpp). `0` is CPU-only for GPU builds. | `0`–`99+` |
| **GPU device** | Optional. When GPUs are detected, pick one or leave default. IDs look like `gpu:0`. Manual Vulkan: `vk:N`. See README multi-GPU section. | empty, `gpu:0`, `vk:0`, … |
| **API key** | Passed as `--api-key` if set. Recommended if you bind to non-loopback. | strong secret or empty |
| **Enable --metrics** | Turns on server metrics if your build supports `--metrics`. | on/off |
| **Local model path / HF repo** | Active model: filesystem path to `.gguf`, or HF repo id for `hf` mode. | `/path/model.gguf`, `org/repo` |
| **Extra args** | Additional tokens passed to `llama-server` (panel-dependent quoting). | e.g. `--threads 8` |

**Presets** (balanced / fast / quality) fill context, GPU layers, and sometimes metrics—they do not replace **Save launch profile**. Click **Save launch profile** after edits so the next **Start** uses them.

---

## Models

- **Current model** shows what will be used on the next server start (from the launch profile).
- **Scan GGUF** refreshes the table from **model roots**.
- **Use** on a row sets `model_mode` to `local`, updates `local_model_path`, and saves the launch profile.
- **Hugging Face download** starts a background job via `huggingface_hub` using a **real file path** in the repo (see the **Files** tab on the model page). It does **not** accept the same string as `llama-server -hf org/repo:quant`: that colon form is **llama.cpp’s** shorthand. Example from Unsloth Qwen3.5-4B: docs may show `llama-server -hf unsloth/Qwen3.5-4B-GGUF:UD-Q4_K_XL` — in the panel use repo **`unsloth/Qwen3.5-4B-GGUF`** and filename **`Qwen3.5-4B-UD-Q4_K_XL.gguf`** (the actual object name on the Hub). When finished, point the launch profile at the downloaded file or HF repo as appropriate. Gated models require `huggingface-cli login` (or `HF_TOKEN`). Job errors are shown in a dedicated block so long messages wrap.

---

## Server

- **Start** spawns `llama-server` with the saved launch profile and bundle `LD_LIBRARY_PATH` behavior.
- **Stop** sends graceful stop to the child.
- **Logs** streams stderr/stdout lines from the supervisor (bounded buffer).

---

## Monitor

Polls `http://<server_host>:<server_port>` for health and related endpoints your `llama-server` build exposes. If the server is stopped or firewalled, panels may be empty or stale.

---

## Tips

- Prefer loopback (`127.0.0.1`) unless you understand network exposure; use an **API key** if you bind broadly.
- Vulkan vs CUDA: GPU selection uses both `CUDA_VISIBLE_DEVICES` and `GGML_VK_VISIBLE_DEVICES` for numeric indices when documented in the app README.
- For upstream behavior and new flags, see [llama.cpp documentation](https://github.com/ggml-org/llama.cpp) and your tarball’s `llama-server --help`.
