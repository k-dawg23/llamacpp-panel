from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass

from huggingface_hub import hf_hub_download


@dataclass
class HfJob:
    id: str
    repo_id: str
    filename: str
    status: str = "pending"
    progress: float = 0.0
    error: str | None = None
    local_path: str | None = None


class HfJobManager:
    def __init__(self) -> None:
        self._jobs: dict[str, HfJob] = {}

    def get(self, job_id: str) -> HfJob | None:
        return self._jobs.get(job_id)

    def start_download(self, repo_id: str, filename: str) -> HfJob:
        job_id = str(uuid.uuid4())
        job = HfJob(id=job_id, repo_id=repo_id, filename=filename)
        self._jobs[job_id] = job

        def run_sync() -> None:
            try:
                job.status = "running"
                path = hf_hub_download(
                    repo_id=repo_id,
                    filename=filename,
                )
                job.local_path = str(path)
                job.progress = 1.0
                job.status = "done"
            except Exception as e:
                job.status = "error"
                job.error = str(e)

        loop = asyncio.get_running_loop()
        loop.run_in_executor(None, run_sync)
        return job
