from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_required_assessment_documents_exist() -> None:
    required_paths = [
        "README.md",
        "docs/01-requirements.md",
        "docs/02-solution.md",
        "docs/03-evaluation.md",
        "docs/04-ai-usage.md",
        "docs/05-retrospective.md",
        "examples/README.md",
        "scripts/record_live_llm_evidence.py",
    ]
    missing = [path for path in required_paths if not (PROJECT_ROOT / path).is_file()]
    assert not missing, f"Missing required files: {missing}"


def test_delivery_documents_match_the_recorded_live_llm_evidence() -> None:
    evaluation = (PROJECT_ROOT / "docs" / "03-evaluation.md").read_text(encoding="utf-8")
    ai_usage = (PROJECT_ROOT / "docs" / "04-ai-usage.md").read_text(encoding="utf-8")
    retrospective = (PROJECT_ROOT / "docs" / "05-retrospective.md").read_text(encoding="utf-8")

    assert "examples/05-live-llm-decision.json" in evaluation
    assert "真实在线调用" in ai_usage
    assert "真实在线 LLM 证据" in retrospective
    assert "未完成真实在线 LLM 调用" not in retrospective
