from __future__ import annotations

from pathlib import Path


def pick_directory(*, title: str, initial_dir: str | None = None) -> str | None:
    try:
        import tkinter as tk
        from tkinter import filedialog
    except Exception as e:  # pragma: no cover - environment dependent
        raise RuntimeError(f"directory picker is unavailable: {e}") from e

    root = tk.Tk()
    root.withdraw()
    try:
        root.attributes("-topmost", True)
    except Exception:
        pass

    initial = (initial_dir or "").strip()
    if initial:
        try:
            initial = str(Path(initial).expanduser().resolve())
        except Exception:
            initial = ""

    try:
        selected = filedialog.askdirectory(
            title=title,
            initialdir=initial or None,
            mustexist=True,
        )
    finally:
        root.destroy()

    if not selected:
        return None
    return str(Path(selected).expanduser().resolve())
