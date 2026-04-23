from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from llamacpp_panel.monitoring import fetch_llama_server_status


@pytest.mark.asyncio
async def test_monitoring_graceful_partial_failure() -> None:
    async def mock_get(url: str, **kwargs):
        if url.endswith("/health"):
            m = MagicMock()
            m.status_code = 200
            m.json = lambda: {"status": "ok"}
            return m
        m = MagicMock()
        m.status_code = 404
        m.text = "no"
        return m

    inner = MagicMock()
    inner.get = AsyncMock(side_effect=mock_get)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=inner)
    mock_cm.__aexit__ = AsyncMock(return_value=None)

    with patch("llamacpp_panel.monitoring.httpx.AsyncClient", return_value=mock_cm):
        out = await fetch_llama_server_status("http://127.0.0.1:8080")

    assert out["health"] == {"status": "ok"}
    assert len(out["errors"]) == 3
