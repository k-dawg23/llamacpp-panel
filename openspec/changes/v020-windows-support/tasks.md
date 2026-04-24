## 1. Release metadata

- [ ] 1.1 Bump `pyproject.toml` and `llamacpp_panel/__init__.py` to **0.2.0**; align `web/package.json` version if required by project convention
- [ ] 1.2 After verification, create and push git tag **`v0.2.0`** (and optional GitHub release notes)

## 2. Cross-platform path and config helpers

- [ ] 2.1 Implement `resolve_llama_server_path` (or successor) that returns `llama-server.exe` on Windows and `llama-server` on POSIX; document any fallback names
- [ ] 2.2 Introduce default config path suitable for Windows (e.g. `platformdirs` / `%LOCALAPPDATA%`) while preserving Linux `XDG_CONFIG_HOME` / `~/.config` behavior; document migration expectations
- [ ] 2.3 Add small `is_windows()` (or equivalent) test seam to avoid scattered `sys.platform` checks

## 3. Supervisor and validation

- [ ] 3.1 Replace `_prepend_ld_path` with host-specific behavior: POSIX → `LD_LIBRARY_PATH` + `:`; Windows → prepend bundle to `PATH` + `;`
- [ ] 3.2 Remove Windows-only false failures from `os.access(..., X_OK)` in supervisor start and `/api/validate-binary`; keep or adjust POSIX checks
- [ ] 3.3 Ensure `validate-binary` subprocess for `--version` uses the same env rules as start (PATH / LD_LIBRARY_PATH)
- [ ] 3.4 Document in README / user guide that **Stop** on Windows is best-effort vs POSIX SIGTERM

## 4. GPU discovery

- [ ] 4.1 Confirm `enumerate_gpus` / `nvidia-smi` invocation works when `nvidia-smi` is only available as `nvidia-smi.exe` (typical Windows); add tests with mocked `subprocess.run` if helpful

## 5. Documentation

- [ ] 5.1 README: Windows 10 + 11 prerequisites, Python version, building the web UI, bundle layout (exe + DLLs), config file location
- [ ] 5.2 Update `docs/panel-user-guide.md` with a short Windows section (paths, GPU, limitations)

## 6. Tests and verification

- [ ] 6.1 Unit tests for executable resolution and env dict (Linux CI with platform mocks)
- [ ] 6.2 Manual smoke on **Windows 10** and **Windows 11**: validate, start, stop, logs, optional multi-GPU if hardware available
- [ ] 6.3 `pytest` and `npm run build` pass on Linux CI
