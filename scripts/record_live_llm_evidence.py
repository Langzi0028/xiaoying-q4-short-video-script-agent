from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from short_video_script_agent.config import Settings
from short_video_script_agent.fixtures.scenarios import p01_request
from short_video_script_agent.graph.workflow import run_request
from short_video_script_agent.llm.client import LiveDecisionEngine


def main() -> None:
    settings = Settings.from_environment()
    if not settings.llm_configured:
        raise SystemExit("LIVE_LLM_NOT_CONFIGURED")

    request = p01_request(target_seconds=30)
    response = run_request(request, decision_engine=LiveDecisionEngine(settings))
    if response.decision_source != "live_llm":
        raise SystemExit("LIVE_LLM_NOT_USED")

    # Keep only business evidence; never serialize local model configuration or prompts.
    payload = {
        "input": request.model_dump(mode="json"),
        "output": response.model_dump(mode="json"),
    }
    destination = PROJECT_ROOT / "examples" / "05-live-llm-decision.json"
    destination.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(destination.name)


if __name__ == "__main__":
    main()

