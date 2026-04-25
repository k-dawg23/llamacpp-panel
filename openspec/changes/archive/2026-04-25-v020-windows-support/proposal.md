## Why

Many operators run local `llama-server` on **Windows 10 and 11** (including older PCs that stay on Win10). The panel today assumes POSIX paths, a bare `llama-server` filename, **`LD_LIBRARY_PATH`** for portable bundles, and **POSIX execute-bit** checks—so supervised launch and validation fail or behave incorrectly on Windows despite the stack (Python, FastAPI, React) being cross-platform. Release **v0.2.0** (tag **`v0.2.0`**) adds an **initial, single-user Windows path** so the same workflow works on Win10/11; **macOS remains out of scope** for this change due to limited test access.

## What Changes

- Bump shipped version to **0.2.0** and document tagging **`v0.2.0`**.
- **Resolve `llama-server` on Windows** (e.g. `llama-server.exe`, documented fallbacks) from the configured bundle directory; keep POSIX behavior unchanged.
- **Replace POSIX-only “executable” gating on Windows** with checks appropriate to the platform (e.g. file exists + readable, optional `--version` probe) so **Validate binary** and **Start** are not blocked by `os.X_OK` semantics.
- **Bundle DLL discovery on Windows:** prepend the bundle directory to the child’s **`PATH`** (or equivalent documented mechanism); keep **`LD_LIBRARY_PATH`** for Linux/POSIX. Document that typical layouts rely on DLLs beside the exe.
- **Stop semantics:** keep **graceful stop** wording for POSIX; document **best-effort** termination on Windows (Python `terminate`/`kill` mapping) without claiming full SIGTERM parity.
- **GPU discovery:** continue using `nvidia-smi` where present; explicitly support **Windows** when the tool is on `PATH` (same CSV query as today).
- **Docs:** README (and user guide as needed): Windows prerequisites, bundle layout, config file location on Windows, and testing note (Win10 + Win11).
- **Tests:** unit tests for path resolution and env selection with **mocked `os.name` / `sys.platform`** (or equivalent) so CI stays Linux-hosted.

## Capabilities

### New Capabilities

- _(none — behavior folded into existing capabilities)_

### Modified Capabilities

- `server-supervisor`: Cross-platform bundle executable resolution, library search env for Windows vs POSIX, validation rules, and clarified stop semantics on Windows.
- `gpu-devices`: Explicit Windows support for NVIDIA enumeration via `nvidia-smi` when available.

## Impact

- **Backend:** `config.py` (`resolve_llama_server_path`), `supervisor.py` (env + spawn), `app.py` (validate-binary probe), possibly small `platform`/`sys` helpers; optional **`platformdirs`** (or minimal equivalent) for default config path on Windows.
- **Frontend:** No required UI redesign; Help/guide text updates if the Markdown is the single source.
- **Docs / release:** README + `docs/panel-user-guide.md`; **`v0.2.0`** tag after verification on real Win10 and Win11 hosts.
- **Compatibility:** **Non-breaking** on Linux; Windows becomes newly supported rather than changing POSIX defaults.
