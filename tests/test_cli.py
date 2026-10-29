import json

from typer.testing import CliRunner

from short_video_script_agent.cli import app


def test_cli_prints_a_single_json_document_to_stdout(tmp_path) -> None:
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

    assert result.exit_code == 0, result.stdout
    payload = json.loads(result.stdout)
    assert payload["status"] == "completed"
    assert payload["material_source_ids"]

