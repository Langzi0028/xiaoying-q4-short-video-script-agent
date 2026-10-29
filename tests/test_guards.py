from short_video_script_agent.fixtures.scenarios import p01_request
from short_video_script_agent.graph.workflow import run_request
from short_video_script_agent.tools.failure_injection import FailureInjector


def test_brand_rule_risk_blocks_without_a_script() -> None:
    response = run_request(p01_request(topic="绝对保证治愈", target_seconds=30))

    assert response.status == "blocked"
    assert response.shots == []
    assert response.risks


def test_unverified_product_fact_blocks_without_a_script() -> None:
    request = p01_request(target_seconds=30).model_copy(
        update={"product_facts": ["P01 保证治愈所有问题"]}
    )
    response = run_request(request)

    assert response.status == "blocked"
    assert response.shots == []
    assert "缺少可验证来源" in response.risks[0]


def test_tool_failure_never_reports_success() -> None:
    response = run_request(
        p01_request(target_seconds=30),
        failure_injector=FailureInjector(fail_actions={"estimate_duration"}),
    )

    assert response.status == "failed"
    assert response.error_code == "TOOL_FAILURE"


def test_execution_limit_returns_explicit_incomplete_status() -> None:
    response = run_request(p01_request(target_seconds=30), max_steps=1)

    assert response.status == "incomplete"
    assert response.error_code == "EXECUTION_LIMIT_REACHED"


def test_trace_has_safe_audit_fields() -> None:
    response = run_request(p01_request(target_seconds=30))

    for event in response.trace:
        assert set(event) >= {
            "node",
            "action",
            "parameters",
            "result_summary",
            "next_action",
            "decision_rationale",
        }
        assert "api_key" not in str(event).lower()
