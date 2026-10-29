from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_examples_include_actual_input_output_and_trace() -> None:
    examples = PROJECT_ROOT / "examples"
    for name in ["01-p01-overlength.md", "02-no-material.md", "03-tool-failure.md"]:
        text = (examples / name).read_text(encoding="utf-8")
        assert "## Input" in text
        assert "## Actual Output" in text
        assert "## Actual Trace" in text


def test_live_llm_evidence_is_safe_when_present() -> None:
    evidence = PROJECT_ROOT / "examples" / "05-live-llm-decision.json"
    if not evidence.exists():
        return
    text = evidence.read_text(encoding="utf-8")
    assert '"decision_source": "live_llm"' in text
    assert "LLM_API_KEY" not in text
    assert "LLM_BASE_URL" not in text
