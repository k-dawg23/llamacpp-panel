from pathlib import Path

from llamacpp_panel.config import AppConfig, LaunchProfile


def test_config_roundtrip(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    cfg = AppConfig(
        llama_bin_dir="/opt/llama",
        model_roots=["/a", "/b"],
        project_folders=["/proj/a", "/proj/b"],
        selected_project_folder="/proj/b",
        launch_profile=LaunchProfile(local_model_path="/m.gguf"),
    )
    cfg.save(p)
    loaded = AppConfig.load(p)
    assert loaded.llama_bin_dir == "/opt/llama"
    assert loaded.model_roots == ["/a", "/b"]
    assert loaded.project_folders == ["/proj/a", "/proj/b"]
    assert loaded.selected_project_folder == "/proj/b"
    assert loaded.launch_profile.local_model_path == "/m.gguf"


def test_config_load_older_file_keeps_new_project_defaults(tmp_path: Path) -> None:
    p = tmp_path / "c.json"
    p.write_text(
        '{\n'
        '  "llama_bin_dir": "/opt/llama",\n'
        '  "model_roots": ["/a"],\n'
        '  "launch_profile": {"local_model_path": "/m.gguf"}\n'
        '}\n',
        encoding="utf-8",
    )
    loaded = AppConfig.load(p)
    assert loaded.project_folders == []
    assert loaded.selected_project_folder == ""
