## Context

The supervisor uses `asyncio.create_subprocess_exec`, resolves `llama-server` as a single POSIX filename, prepends the bundle directory to **`LD_LIBRARY_PATH`**, and uses **`os.access(..., X_OK)`** before start/validate. Windows ignores `LD_LIBRARY_PATH` for native PE binaries, expects **`llama-server.exe`**, and does not treat “executable” like Unix. Stop uses **`terminate()`**, which maps to a weaker graceful story on Windows than SIGTERM on Linux.

Operators target **Windows 10 and 11** with the same single-user, localhost-first panel. **macOS is explicitly deferred** (Metal, dyld policy, no test hardware).

## Goals / Non-Goals

**Goals:**

- **Win10 + Win11:** From source install (`pip install -e .`, built web UI), user can set bundle dir, validate, start/stop, stream logs, and use GPU enumeration when `nvidia-smi` works.
- **POSIX unchanged:** Linux behavior and tests remain the default CI path.
- **Documented limitations:** Weaker graceful shutdown on Windows; AV/long-path edge cases called out in docs.
- **Version 0.2.0** and tag **`v0.2.0`**.

**Non-Goals:**

- macOS support, code signing, Microsoft Store packaging, or Windows Service integration.
- Perfect parity with POSIX signal semantics.
- Automatic download of `llama-server` for Windows.
- WSL-as-target vs native Windows detection UX (docs may mention “use native Windows binaries with native Python”).

## Decisions

1. **Executable resolution:** On Windows, try `llama-server.exe` first, then optional documented fallbacks (`llama-server` if present). On POSIX, keep `llama-server` (and document distro packages that rename binaries as a manual path workaround).
2. **Library loading:** **POSIX:** keep prepending to `LD_LIBRARY_PATH` with `:` separator. **Windows:** prepend absolute bundle dir to child **`PATH`** with `;` separator (document). Rely on “DLLs next to exe” for many upstream layouts; PATH prepend covers extra DLLs in the same folder when the loader searches PATH.
3. **Readiness check:** **POSIX:** keep `is_file` + `X_OK` or align with existing behavior. **Windows:** `is_file` + not a directory; optionally treat successful `--version` subprocess as stronger signal; do **not** require `X_OK`.
4. **Config directory:** Prefer **`platformdirs`** (or small wrapper) so default config on Windows uses `%LOCALAPPDATA%` (or `APPDATA`) under a `llamacpp-panel` subfolder, while preserving `XDG_CONFIG_HOME` / `~/.config` on Linux. Migration: if old path exists, optional read fallback on first load (design choice at implement: simplest is “new default only” with README note—call out in tasks).
5. **Tests:** Use `unittest.mock` to patch `sys.platform` / `os.name` (or inject a tiny `is_windows()` helper) for resolution and env builder logic without requiring a Windows runner in CI.
6. **GPU:** No change to CSV format; ensure `nvidia-smi` invocation uses `shell=False` and relies on PATH (`.exe` resolved by Windows).

## Risks / Trade-offs

- **PATH pollution:** Prepending bundle to `PATH` could shadow other tools—acceptable for a short-lived child process scoped to the supervisor.
- **terminate() on Windows:** Harder shutdown may rarely leave GPU memory stuck—mitigate with docs and optional longer timeout before `kill`.
- **Dual config path:** If Windows moves to `%LOCALAPPDATA%`, existing Linux configs unaffected; Windows users upgrading from a hypothetical older “~/.config” copy need README guidance.
- **Antivirus / SmartScreen:** First run may delay subprocess—document; consider slightly longer timeouts for `--version` on Windows only.

## Migration Plan

- Ship **0.2.0**; Linux users see no config migration requirement if defaults unchanged.
- Windows new installs follow README; tag **`v0.2.0`** after manual smoke on Win10 and Win11.

## Open Questions

- Whether to add **read fallback** from `~/.config/llamacpp-panel/config.json` on Windows for cross-platform dotfile users (probably **no** in v0.2.0 unless trivial).
- Exact list of **alternate** llama.cpp Windows binary names beyond `llama-server.exe` (spike against common release zips).
