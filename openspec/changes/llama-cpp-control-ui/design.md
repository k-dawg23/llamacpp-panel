## Context

The repository targets a companion application for [llama.cpp](https://github.com/ggml-org/llama.cpp) on **Ubuntu 24.04**. Users often install prebuilt bundles (for example Vulkan tarballs) where `llama-server` and `libggml-*.so` live in the same directory, requiring `LD_LIBRARY_PATH` when spawning the binary. Day-to-day tasks—picking a GGUF, pulling from Hugging Face, tuning flags, and confirming the server is healthy—are split across the shell, browser, and upstream docs. The proposal introduces a **localhost-first control panel** with a **supervisor** that owns the `llama-server` process and a **frontend** for friendly configuration and visibility.

## Goals / Non-Goals

**Goals:**

- Provide a **single local entrypoint** (web UI) to configure the llama.cpp binary location, compose common `llama-server` options, start and stop the server, and inspect logs.
- Support **local GGUF discovery** and **Hugging Face GGUF download** into layouts compatible with upstream’s HF cache behavior.
- Surface **runtime status** using `llama-server`’s HTTP API (`/health`, `/props`, `/slots`, and optional `/metrics` when enabled).
- Default to **loopback** networking for both the supervisor and guidance for `llama-server` bind addresses.

**Non-Goals:**

- Shipping or forking llama.cpp; no requirement to patch upstream.
- Replacing the upstream chat WebUI; this tool focuses on **operations** (models, flags, lifecycle, observability).
- Remote multi-host cluster orchestration or authenticated multi-user tenancy in v1.
- Automatic GPU driver or Vulkan/CUDA installation.

## Decisions

1. **Web UI + local supervisor API (recommended default)**  
   - **Rationale:** Forms, log streaming, and status dashboards map naturally to a browser; the supervisor runs on a separate localhost port from `llama-server`.  
   - **Alternatives:** Terminal UI only (harder HF discovery and log UX); Electron shell (heavier packaging for v1).

2. **Supervisor backend in Python (FastAPI + uvicorn)**  
   - **Rationale:** Strong ecosystem for subprocess management, file scanning, and `huggingface_hub` for downloads; straightforward on Ubuntu.  
   - **Alternatives:** Node + `huggingface-cli` subprocess (more moving parts); Go (faster binary, slower iteration for HF integration).

3. **Frontend with Vite + React (or Svelte)**  
   - **Rationale:** Mature component patterns for settings and live updates (SSE or WebSocket from supervisor for logs).  
   - **Alternatives:** Server-rendered templates (slower iteration for rich UI).

4. **Process model: one supervised `llama-server` child**  
   - **Rationale:** Matches single-machine hobbyist and workstation use; simplifies port and log ownership.  
   - **Alternatives:** External systemd only (less discoverable from UI); multiple instances (defer).

5. **Configuration persistence: JSON or YAML in XDG config dir**  
   - **Rationale:** Standard on Linux; easy to back up and version. Store binary directory, last launch profile, model roots, and supervisor listen address.

6. **Library path handling**  
   - **Rationale:** When the user points at a bundle directory containing `llama-server` and sibling `.so` files, the supervisor SHALL prepend that directory to `LD_LIBRARY_PATH` for the child process only (not globally).  
   - **Alternatives:** Require system-wide `ldconfig` (fragile for portable bundles).

7. **Monitoring via HTTP client to user-configured `llama-server` base URL**  
   - **Rationale:** Decouples supervisor from parsing logs for state; aligns with [server README](https://github.com/ggml-org/llama.cpp/blob/master/tools/server/README.md) endpoints.  
   - **Alternatives:** Parse stdout only (brittle).

## Risks / Trade-offs

- **[Risk] Upstream CLI and HTTP API drift across releases** → **Mitigation:** Display detected `llama-server --version`; treat optional endpoints gracefully; document minimum tested version.  
- **[Risk] Vulkan vs CUDA vs CPU-only binary mismatch** → **Mitigation:** User selects bundle path; supervisor validates binary exists and is executable; surface clear errors from failed launch.  
- **[Risk] HF downloads are large and slow** → **Mitigation:** Progress reporting, resumable downloads via `huggingface_hub`, disk space checks where feasible.  
- **[Risk] Binding `llama-server` to non-loopback without API key** → **Mitigation:** Warn in UI; surface `--api-key` when host is not localhost.  
- **[Trade-off] Single supervised process** → Power users running multiple servers still use manual tooling until a later phase.

## Migration Plan

- **Deploy:** Install Python deps and Node build toolchain (or consume a future packaged release); run supervisor; open browser to configured localhost URL.  
- **Rollback:** Stop supervisor and any child `llama-server`; remove or ignore app config; continue using raw `llama-server` from the shell (no data migration required).  
- **Config:** First-run wizard captures binary directory and optional model roots; existing manual setups remain valid.

## Open Questions

- Exact frontend framework (React vs Svelte) and component library.  
- Whether v1 includes a generated **systemd user unit** or only documents it.  
- Authentication between frontend and supervisor (likely unnecessary on strict localhost; revisit if LAN exposure is added).
