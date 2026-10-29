from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from short_video_script_agent.fixtures.scenarios import p01_request, unmatched_request
from short_video_script_agent.graph.workflow import run_request
from short_video_script_agent.tools.failure_injection import FailureInjector


EXAMPLES = PROJECT_ROOT / "examples"


def _write_example(name: str, request, **kwargs) -> None:
    response = run_request(request, **kwargs)
    payload = response.model_dump(mode="json")
    document = "\n".join(
        [
            f"# {name}",
            "",
            "## Input",
            "```json",
            json.dumps(request.model_dump(mode="json"), ensure_ascii=False, indent=2),
            "```",
            "",
            "## Actual Output",
            "```json",
            json.dumps({key: value for key, value in payload.items() if key != "trace"}, ensure_ascii=False, indent=2),
            "```",
            "",
            "## Actual Trace",
            "```json",
            json.dumps(payload["trace"], ensure_ascii=False, indent=2),
            "```",
            "",
        ]
    )
    (EXAMPLES / f"{name}.md").write_text(document, encoding="utf-8")


def main() -> None:
    EXAMPLES.mkdir(exist_ok=True)
    _write_example("01-p01-overlength", p01_request(target_seconds=30))
    _write_example("02-no-material", unmatched_request())
    _write_example(
        "03-tool-failure",
        p01_request(target_seconds=30),
        failure_injector=FailureInjector(fail_actions={"estimate_duration"}),
    )
    _write_example("04-execution-limit", p01_request(target_seconds=30), max_steps=1)


if __name__ == "__main__":
    main()
