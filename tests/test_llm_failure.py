from typer.testing import CliRunner

from short_video_script_agent.cli import app


def test_live_llm_failure_prints_only_exception_type_then_falls_back(monkeypatch, tmp_path) -> None:
    class BrokenEngine:
        def choose(self, legal_actions, state):
            raise TimeoutError("gateway details must not leak")

    monkeypatch.setattr("short_video_script_agent.cli._decision_engine", lambda: BrokenEngine())
    result = CliRunner().invoke(
        app,
        [
            "run",
            "--topic",
            "P01 字幕功能",
            "--audience",
            "短视频创作者",
            "--target-seconds",
            "30",
            "--style",
            "轻快",
            "--material-id",
            "P01",
            "--database",
            str(tmp_path / "runs.db"),
        ],
    )

    assert result.exit_code == 0
    assert '"decision_source":"fallback"' in result.stdout
    assert "LLM request failed: TimeoutError; using deterministic fallback." in result.stderr
    assert "gateway details" not in result.stderr
