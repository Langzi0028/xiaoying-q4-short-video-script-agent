from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_root_entrypoint_and_required_runtime_paths_exist() -> None:
    required_paths = [
        "main.py",
        "short_video_script_agent/__init__.py",
        "data/.gitkeep",
        ".env.example",
        ".gitignore",
        "requirements.txt",
    ]

    missing = [path for path in required_paths if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing required paths: {missing}"


def test_main_entrypoint_delegates_to_the_cli() -> None:
    entrypoint = (PROJECT_ROOT / "main.py").read_text(encoding="utf-8")

    assert "from short_video_script_agent.cli import main" in entrypoint
    assert 'if __name__ == "__main__":' in entrypoint
    assert "main()" in entrypoint

