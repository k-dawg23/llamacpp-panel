from __future__ import annotations

import asyncio
from collections import deque
from typing import Callable


class RingBuffer:
    def __init__(self, max_lines: int) -> None:
        self._max = max(100, max_lines)
        self._lines: deque[str] = deque(maxlen=self._max)

    def append(self, line: str) -> None:
        self._lines.append(line)

    def snapshot(self) -> list[str]:
        return list(self._lines)


class LogBroadcaster:
    """Broadcast log lines to multiple SSE subscribers."""

    def __init__(self) -> None:
        self._queues: list[asyncio.Queue[str]] = []

    def subscribe(self, maxsize: int = 2000) -> asyncio.Queue[str]:
        q: asyncio.Queue[str] = asyncio.Queue(maxsize=maxsize)
        self._queues.append(q)
        return q

    def unsubscribe(self, q: asyncio.Queue[str]) -> None:
        try:
            self._queues.remove(q)
        except ValueError:
            pass

    def publish(self, line: str) -> None:
        for q in list(self._queues):
            try:
                q.put_nowait(line)
            except asyncio.QueueFull:
                pass
