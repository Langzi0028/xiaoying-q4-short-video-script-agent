import pytest
from pydantic import ValidationError

from short_video_script_agent.models import ScriptRequest, ScriptResponse, Shot


def test_request_rejects_non_positive_target_seconds() -> None:
    with pytest.raises(ValidationError):
        ScriptRequest(
            topic="字幕功能",
            audience="短视频创作者",
            target_seconds=0,
            style="轻快",
        )


def test_request_accepts_optional_product_facts_and_brand_rules() -> None:
    request = ScriptRequest(
        topic="P01 字幕功能",
        audience="短视频创作者",
        target_seconds=30,
        style="轻快",
        product_facts=["P01 支持字幕"],
        brand_rules=["不得使用绝对化表达"],
    )

    assert request.product_facts == ["P01 支持字幕"]
    assert request.brand_rules == ["不得使用绝对化表达"]


def test_response_contains_every_required_delivery_field() -> None:
    response = ScriptResponse(
        run_id="run-demo",
        status="completed",
        title="支持字幕，让表达更清晰",
        shots=[
            Shot(
                index=1,
                visual_description="展示字幕开关",
                voiceover="打开字幕功能",
                subtitle="支持字幕",
                estimated_seconds=8,
                material_source_ids=["P01-01"],
            )
        ],
        total_estimated_seconds=8,
        material_source_ids=["P01-01"],
        risks=[],
        decision_source="fallback",
        trace=[],
    )

    assert set(response.model_dump()) >= {
        "status",
        "title",
        "shots",
        "total_estimated_seconds",
        "material_source_ids",
        "risks",
        "decision_source",
        "trace",
    }
