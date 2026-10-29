from short_video_script_agent.fixtures.scenarios import p01_request, unmatched_request
from short_video_script_agent.graph.workflow import run_request


def test_p01_overlength_draft_is_compressed_and_reestimated() -> None:
    response = run_request(p01_request(target_seconds=30))

    assert response.status == "completed"
    assert response.total_estimated_seconds <= 30
    assert response.material_source_ids
    assert [event["action"] for event in response.trace] == [
        "check_rules",
        "search_materials",
        "build_draft",
        "estimate_duration",
        "compress_draft",
        "estimate_duration",
        "finish",
    ]


def test_no_search_results_rewrites_once_then_requests_information() -> None:
    response = run_request(unmatched_request())

    assert response.status == "needs_info"
    assert response.material_source_ids == []
    assert "未找到" in response.message
    assert [event["action"] for event in response.trace] == [
        "check_rules",
        "search_materials",
        "rewrite_search",
        "search_materials",
        "request_more_info",
    ]
