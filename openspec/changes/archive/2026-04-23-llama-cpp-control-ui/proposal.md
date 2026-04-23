## Why

Running [llama.cpp](https://github.com/ggml-org/llama.cpp) effectively on Linux still requires juggling binary paths (and `LD_LIBRARY_PATH` for prebuilt bundles), long `llama-server` flag lists, Hugging Face GGUF discovery, and separate tools to watch logs and health. A small, user-friendly control layer in this repo reduces friction for daily use on Ubuntu 24.04 and makes server lifecycle and model management approachable without memorizing CLI details.

## What Changes

- Introduce a **local control application** (web UI plus a thin backend) that lives under `/home/kdawg/AI/Cursor/llama_front_end/`, focused on **settings**, **model acquisition**, and **supervising `llama-server`**.
- **Configure** the install: user-selectable directory containing `llama-server` (defaulting to a sensible path such as an unpacked release bundle), with automatic use of bundled shared libraries where needed.
- **Model workflows**: browse or scan local `.gguf` files; download GGUF artifacts from Hugging Face into the standard cache layout compatible with llama.cpp `-hf` usage.
- **Server lifecycle**: start and stop `llama-server` as a managed child process; stream stdout/stderr for troubleshooting; persist last-used arguments and profiles.
- **Monitoring**: surface `llama-server` status using its HTTP API (for example health, properties, and slot state), with optional metrics when enabled on the server.
- No change to upstream llama.cpp itself; this repo becomes a **downstream companion** that shells out to and talks to existing binaries.

## Capabilities

### New Capabilities

- `server-supervisor`: Configurable llama.cpp runtime paths, building and launching `llama-server`, graceful shutdown, log capture, and persisted launch profiles.
- `model-library`: Discover local GGUF models; search or resolve Hugging Face repos/files; download and reconcile with the HF cache used by llama.cpp.
- `server-monitoring`: Read-only integration with `llama-server` HTTP endpoints for health and operational visibility (and optional Prometheus-style metrics when enabled).
- `control-panel-ui`: Localhost-first web UI for settings, model picking, start/stop controls, log tail, and status dashboards; communicates only with the local supervisor API and the user’s `llama-server` instance.

### Modified Capabilities

- None (no existing capability specs in `openspec/specs/`).

## Impact

- **New dependencies**: application runtime for the supervisor (for example Python with FastAPI/uvicorn or Node) and frontend build tooling (for example Vite); optional `huggingface_hub` or HF CLI for downloads.
- **System interaction**: subprocess management, file system access for models and config, optional environment variables (`LD_LIBRARY_PATH`) when using bundled `.so` layouts.
- **Security posture**: default bind addresses on loopback; optional passthrough of `llama-server` API keys when exposing non-local access.
- **Documentation**: user-facing notes for Ubuntu 24.04 setup, Vulkan vs CUDA bundles, and compatibility with upstream server API changes across llama.cpp versions.
