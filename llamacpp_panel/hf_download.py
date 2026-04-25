from __future__ import annotations

import asyncio
import threading
import uuid
from dataclasses import dataclass
from io import StringIO

from huggingface_hub import hf_hub_download
from tqdm.auto import tqdm


@dataclass
class HfJob:
    id: str
    repo_id: str
    filename: str
    status: str = "pending"
    progress: float = 0.0
    error: str | None = None
    local_path: str | None = None


def _tqdm_factory(lock: threading.Lock, job: HfJob) -> type[tqdm]:
    """Build a tqdm subclass that forwards progress into ``job.progress`` (thread-safe)."""

    class TqdmForJob(tqdm):
        def __init__(self, *args, **kwargs) -> None:  # type: ignore[no-untyped-def]
            kwargs.setdefault("file", StringIO())
            super().__init__(*args, **kwargs)

        def update(self, n: float = 1) -> bool | None:  # type: ignore[no-untyped-def]
            r = super().update(n)
            total = self.total
            with lock:
                if total:
                    job.progress = min(0.999, float(self.n) / float(total))
                elif self.n > 0:
                    job.progress = max(job.progress, 0.05)
            return r

    return TqdmForJob


class HfJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, HfJob] = {}
        self._lock = threading.Lock()

    def get(self, job_id: str) -> HfJob | None:
        with self._lock:
            j = self._jobs.get(job_id)
            if j is None:
                return None
            return HfJob(
                id=j.id,
                repo_id=j.repo_id,
                filename=j.filename,
                status=j.status,
                progress=j.progress,
                error=j.error,
                local_path=j.local_path,
            )

    def start_download(self, repo_id: str, filename: str) -> HfJob:
        job_id = str(uuid.uuid4())
        job = HfJob(id=job_id, repo_id=repo_id, filename=filename)
        with self._lock:
            self._jobs[job_id] = job

        lock = self._lock

        def run_sync() -> None:
            try:
                with lock:
                    job.status = "running"
                    job.progress = 0.0
                tqdm_cls = _tqdm_factory(lock, job)
                path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                    tqdm_class=tqdm_cls,
                )
                with lock:
                    job.local_path = str(path)
                    job.progress = 1.0
                    job.status = "done"
            except Exception as e:
                with lock:
                    job.status = "error"
                    job.error = str(e)

        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, run_sync)
        return job
