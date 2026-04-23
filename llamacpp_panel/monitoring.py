from __future__ import annotations

from typing import Any

import httpx


async def fetch_llama_server_status(
    base_url: str,
    *,
    api_key: str | None = None,
    timeout: float = 5.0,
) -> dict[str, Any]:
    """Aggregate /health, /props, /slots, /metrics from llama-server."""
    base = base_url.rstrip("/")
    headers: dict[str, str] = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    out: dict[str, Any] = {
        "base_url": base,
        "health": None,
        "props": None,
        "slots": None,
        "metrics": None,
        "errors": [],
    }

    async with httpx.AsyncClient(timeout=timeout) as client:
        for name, path in (
            ("health", "/health"),
            ("props", "/props"),
            ("slots", "/slots"),
            ("metrics", "/metrics"),
        ):
            try:
                r = await client.get(f"{base}{path}", headers=headers)
                if r.status_code == 200:
                    if name == "metrics":
                        out[name] = r.text
                    else:
                        try:
                            out[name] = r.json()
                        except Exception:
                            out[name] = r.text
                else:
                    out["errors"].append(
                        {"endpoint": path, "status": r.status_code, "detail": r.text[:500]},
                    )
            except httpx.RequestError as e:
                out["errors"].append({"endpoint": path, "error": str(e)})

    return out
