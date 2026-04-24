from __future__ import annotations

import sys
from pathlib import Path


def is_windows() -> bool:
    """True when running on native Windows (not WSL)."""
    return sys.platform == "win32"


def apply_bundle_library_env(env: dict[str, str], bundle_dir: Path) -> None:
    """Ensure the supervised child can load bundled shared libraries.

    POSIX: prepend ``bundle_dir`` to ``LD_LIBRARY_PATH`` (``:`` separator).
    Windows: prepend ``bundle_dir`` to ``PATH`` (``;`` separator); ``LD_LIBRARY_PATH``
    is not used for native PE binaries.
    """
    prefix = str(bundle_dir.resolve())
    if is_windows():
        key = "PATH"
        prev = env.get(key, "")
        env[key] = f"{prefix};{prev}" if prev else prefix
    else:
        key = "LD_LIBRARY_PATH"
        prev = env.get(key, "")
        env[key] = f"{prefix}:{prev}" if prev else prefix
