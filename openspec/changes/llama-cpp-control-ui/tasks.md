## 1. Repository and runtime scaffolding

- [x] 1.1 Add Python project layout for the supervisor (for example `pyproject.toml`, virtualenv notes, entry module).
- [x] 1.2 Add frontend app scaffold (Vite + chosen framework) under a `web/` or `frontend/` directory with dev and production build scripts.
- [x] 1.3 Document Ubuntu 24.04 prerequisites (Python version, Node, optional Vulkan drivers) in a short root README.

## 2. Configuration and persistence

- [x] 2.1 Implement persistent app config (XDG config path) for binary directory, model roots, supervisor bind host/port, and last launch profile.
- [x] 2.2 Implement validation API: resolve `llama-server` path, check executable, optionally capture `--version` output for display.

## 3. Server supervisor core

- [x] 3.1 Implement argument builder from launch profile (local `-m` vs `-hf`, host, port, context, GPU layers, metrics flag, API key, extra args).
- [x] 3.2 Spawn `llama-server` with merged environment (`LD_LIBRARY_PATH` prepend for bundle dir) and capture stdout/stderr to a bounded buffer.
- [x] 3.3 Implement graceful stop (SIGTERM), crash detection, and expose supervised state via REST or RPC consumed by the UI.
- [x] 3.4 Add log streaming endpoint (SSE or WebSocket) for the UI.

## 4. Model library

- [x] 4.1 Implement async directory scan for `.gguf` with size and mtime; configurable roots.
- [x] 4.2 Integrate Hugging Face downloads via `huggingface_hub` with progress events surfaced to the API.
- [x] 4.3 Wire API responses to list local models and download status for the UI.

## 5. Monitoring

- [x] 5.1 Implement HTTP client helpers for `llama-server` `/health`, `/props`, `/slots`, and optional `/metrics` with graceful degradation when disabled.
- [x] 5.2 Expose aggregated status JSON for the dashboard poll loop.

## 6. Control panel UI

- [x] 6.1 Build settings view: binary path, model roots, server host/port, API key, common flags, presets.
- [x] 6.2 Build model library view: list local GGUF, HF download form, select active model.
- [x] 6.3 Build operations view: start/stop, connection state, validation messages.
- [x] 6.4 Build monitoring view: health, summarized props/slots, optional raw metrics panel.
- [x] 6.5 Build live log panel subscribed to the streaming endpoint.

## 7. Integration and polish

- [x] 7.1 Serve built static frontend from the supervisor in production mode; proxy API during development.
- [x] 7.2 Manual end-to-end test on Ubuntu against a real `llama-server` bundle (for example Vulkan tarball layout).
- [x] 7.3 Add basic automated tests for argument building, config load/save, and monitoring client error handling.
