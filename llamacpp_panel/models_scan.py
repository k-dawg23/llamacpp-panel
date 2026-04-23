from __future__ import annotations

import asyncio
from pathlib import Path

from pydantic import BaseModel


class GgufEntry(BaseModel):
    path: str
    size_bytes: int
    mtime: float


async def scan_gguf_roots(roots: list[str], max_depth: int = 8) -> list[GgufEntry]:
    """Scan directories for .gguf files (run blocking work in executor)."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, lambda: _scan_sync(roots, max_depth))


def _scan_sync(roots: list[str], max_depth: int) -> list[GgufEntry]:
    found: list[GgufEntry] = []
    for raw in roots:
        root = Path(raw).expanduser().resolve()
        if not root.is_dir():
            continue
        for p in root.rglob("*.gguf"):
            try:
                rel_depth = len(p.relative_to(root).parts)
                if rel_depth > max_depth:
                    continue
            except ValueError:
                continue
            try:
                st = p.stat()
            except OSError:
                continue
            found.append(
                GgufEntry(path=str(p), size_bytes=st.st_size, mtime=st.st_mtime),
            )
    found.sort(key=lambda e: e.path.lower())
    return found
