from __future__ import annotations

from ..models import Material, ScriptRequest


MATERIALS = [
    Material(
        source_id="P01-01",
        product_id="P01",
        title="字幕开关演示",
        keywords=["字幕", "支持字幕", "创作者", "P01"],
        fact="P01 支持字幕",
        visual="创作者在编辑页打开字幕开关，成片出现清晰字幕",
        duration_seconds=14,
    ),
    Material(
        source_id="P01-02",
        product_id="P01",
        title="字幕效果展示",
        keywords=["字幕", "支持字幕", "表达", "P01"],
        fact="P01 支持字幕",
        visual="成片中字幕随旁白同步出现",
        duration_seconds=12,
    ),
    Material(
        source_id="P01-03",
        product_id="P01",
        title="编辑流程收尾",
        keywords=["字幕", "编辑", "P01"],
        fact="P01 支持字幕",
        visual="完成字幕编辑后预览短片",
        duration_seconds=12,
    ),
]


def p01_request(*, topic: str = "P01 字幕功能", target_seconds: int = 30) -> ScriptRequest:
    return ScriptRequest(
        topic=topic,
        audience="短视频创作者",
        target_seconds=target_seconds,
        style="轻快",
        material_id="P01",
    )


def unmatched_request() -> ScriptRequest:
    return ScriptRequest(
        topic="量子护肤配方",
        audience="短视频创作者",
        target_seconds=30,
        style="专业",
    )

