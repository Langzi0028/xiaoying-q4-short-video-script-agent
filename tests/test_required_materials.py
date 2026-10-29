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
