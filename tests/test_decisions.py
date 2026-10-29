from short_video_script_agent.llm.decision_tools import (
    Decision,
    FallbackDecisionEngine,
    validate_decision,
)
from short_video_script_agent.enums import DecisionSource
from short_video_script_agent.fixtures.scenarios import p01_request
from short_video_script_agent.graph.workflow import run_request


def test_invalid_model_action_falls_back_to_a_legal_action() -> None:
    decision = validate_decision(
        Decision(action="invent_material", rationale="not allowed", source="live_llm"),
        legal_actions=["request_more_info", "finish"],
        fallback_action="request_more_info",
    )

    assert decision.action == "request_more_info"
    assert decision.source == "fallback"


def test_fallback_changes_action_after_duration_tool_result() -> None:
    engine = FallbackDecisionEngine()

    assert engine.choose(["compress_draft", "finish"], {"duration": 38, "target_seconds": 30}).action == "compress_draft"
    assert engine.choose(["compress_draft", "finish"], {"duration": 30, "target_seconds": 30}).action == "finish"


def test_live_decision_source_is_recorded_after_a_legal_online_choice() -> None:
    class LegalLiveEngine:
        def choose(self, legal_actions, state):
            action = "compress_draft" if "compress_draft" in legal_actions else legal_actions[0]
            return Decision(action=action, rationale="online decision", source=DecisionSource.LIVE_LLM)

    response = run_request(p01_request(target_seconds=30), decision_engine=LegalLiveEngine())

    assert response.status == "completed"
    assert response.decision_source == DecisionSource.LIVE_LLM
    assert response.trace[3].next_action == "compress_draft"


def test_no_result_decision_can_request_more_information_without_a_rewrite() -> None:
    from short_video_script_agent.fixtures.scenarios import unmatched_request

    class RequestInfoEngine:
        def choose(self, legal_actions, state):
            action = "request_more_info" if "request_more_info" in legal_actions else legal_actions[0]
            return Decision(action=action, rationale="need more context", source=DecisionSource.LIVE_LLM)

    response = run_request(unmatched_request(), decision_engine=RequestInfoEngine())

    assert response.status == "needs_info"
    assert [event.action for event in response.trace] == [
        "check_rules",
        "search_materials",
        "request_more_info",
    ]
    assert response.trace[1].next_action == "request_more_info"
