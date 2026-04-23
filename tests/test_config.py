from pathlib import Path

from llamacpp_panel.config import AppConfig, LaunchProfile


def test_config_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    cfg = AppConfig(
        llama_bin_dir="/opt/llama",
        model_roots=["/a", "/b"],
        launch_profile=LaunchProfile(local_model_path="/m.gguf"),
    )
    cfg.save(p)
    loaded = AppConfig.load(p)
    assert loaded.llama_bin_dir == "/opt/llama"
    assert loaded.model_roots == ["/a", "/b"]
    assert loaded.launch_profile.local_model_path == "/m.gguf"
