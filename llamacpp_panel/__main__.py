from __future__ import annotations

from pathlib import Path

import uvicorn

from llamacpp_panel.app import create_app
from llamacpp_panel.config import AppConfig


def main() -> None:
    repo_root = Path(__file__).resolve().parent.parent
    web_dist = repo_root / "web" / "dist"
    cfg = AppConfig.load()

    uvicorn.run(
        create_app(web_dist=web_dist if web_dist.is_dir() else None),
        host=cfg.supervisor_host,
        port=cfg.supervisor_port,
    )


if __name__ == "__main__":
    main()
