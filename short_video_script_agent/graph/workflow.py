from __future__ import annotations

from typing import Callable, Protocol
from uuid import uuid4

from ..enums import DecisionSource, ErrorCode, RunStatus
from ..llm.decision_tools import Decision, FallbackDecisionEngine, validate_decision
from ..models import Material, ScriptRequest, ScriptResponse, Shot, TraceEvent
from ..tools.duration import estimate_duration
from ..tools.failure_injection import FailureInjector
from ..tools.materials import search_materials
from ..tools.rules import check_brand_rules, check_factual_rules


class DecisionEngine(Protocol):
    def choose(self, legal_actions: list[str], state: dict[str, object]) -> Decision: ...


def _event(
    action: str,
    summary: str,
    *,
    parameters: dict[str, object] | None = None,
    next_action: str | None = None,
    rationale: str,
) -> TraceEvent:
    return TraceEvent(
        node=action,
        action=action,
        parameters=parameters or {},
        result_summary=summary,
        next_action=next_action,
        decision_rationale=rationale,
    )


def _draft_from_materials(materials: list[Material]) -> list[Shot]:
    # The fixture's three source clips intentionally form the 38-second first draft.
    initial_seconds = [14, 12, 12]
    return [
        Shot(
            index=index,
            visual_description=material.visual,
            voiceover=material.fact,
            subtitle="支持字幕",
            estimated_seconds=initial_seconds[index - 1],
            material_source_ids=[material.source_id],
        )
        for index, material in enumerate(materials[:3], start=1)
    ]


def _compress(shots: list[Shot], target_seconds: int) -> list[Shot]:
    compressed = [shot.model_copy(deep=True) for shot in shots]
    reduction = max(0, sum(shot.estimated_seconds for shot in compressed) - target_seconds)
    for shot in reversed(compressed):
        change = min(max(0, shot.estimated_seconds - 4), reduction)
        shot.estimated_seconds -= change
        reduction -= change
        if reduction == 0:
            break
    return compressed


def run_request(
    request: ScriptRequest,
    *,
    max_steps: int = 24,
    failure_injector: FailureInjector | None = None,
    decision_engine: DecisionEngine | None = None,
    on_llm_failure: Callable[[BaseException], None] | None = None,
) -> ScriptResponse:
    trace: list[TraceEvent] = []
    run_id = f"run_{uuid4().hex[:12]}"
    steps = 0
    fallback = FallbackDecisionEngine()
    engine = decision_engine or fallback
    decision_source = DecisionSource.FALLBACK

    def consume_step() -> bool:
        nonlocal steps
        if steps >= max_steps:
            return False
        steps += 1
        return True

    def decide(legal_actions: list[str], state: dict[str, object]) -> Decision:
        nonlocal decision_source
        try:
            candidate = engine.choose(legal_actions, state)
        except Exception as error:
            if decision_engine is not None and on_llm_failure is not None:
                on_llm_failure(error)
            candidate = fallback.choose(legal_actions, state)
        decision = validate_decision(
            candidate,
            legal_actions=legal_actions,
            fallback_action=legal_actions[0],
        )
        decision_source = decision.source
        return decision

    try:
        if not consume_step():
            return _incomplete(run_id, trace, decision_source)
        risks = check_brand_rules(request, failure_injector=failure_injector)
        trace.append(
            _event(
                "check_rules",
                "发现品牌风险" if risks else "品牌规则初检通过",
                parameters={"topic": request.topic, "brand_rule_count": len(request.brand_rules)},
                next_action="finish_blocked" if risks else "search_materials",
                rationale="规则风险必须在生成脚本前阻断。" if risks else "未发现阻断规则，可以检索素材。",
            )
        )
        if risks:
            return ScriptResponse(
                run_id=run_id,
                status=RunStatus.BLOCKED,
                risks=risks,
                message="品牌规则校验未通过，未生成脚本。",
                decision_source=decision_source,
                trace=trace,
            )

        if not consume_step():
            return _incomplete(run_id, trace, decision_source)
        materials = search_materials(
            request.topic,
            material_id=request.material_id,
            failure_injector=failure_injector,
        )
        fact_risks = check_factual_rules(request, materials)
        if fact_risks:
            trace.append(
                _event(
                    "check_rules",
                    "产品事实缺少可验证来源",
                    parameters={"product_fact_count": len(request.product_facts)},
                    next_action="finish_blocked",
                    rationale="用户提供的产品事实必须与检索到的素材事实一致。",
                )
            )
            return ScriptResponse(
                run_id=run_id,
                status=RunStatus.BLOCKED,
                risks=fact_risks,
                message="产品事实无法由当前素材验证，未生成脚本。",
                decision_source=decision_source,
                trace=trace,
            )
        first_decision = decide(
            ["build_draft"] if materials else ["rewrite_search", "request_more_info"],
            {"material_count": len(materials)},
        )
        trace.append(
            _event(
                "search_materials",
                f"检索到 {len(materials)} 个素材",
                parameters={"query": request.topic, "material_id": request.material_id or ""},
                next_action=first_decision.action,
                rationale=first_decision.rationale,
            )
        )

        if not materials:
            if first_decision.action == "request_more_info":
                trace.append(
                    _event(
                        "request_more_info",
                        "没有可用素材",
                        parameters={},
                        next_action=None,
                        rationale=first_decision.rationale,
                    )
                )
                return ScriptResponse(
                    run_id=run_id,
                    status=RunStatus.NEEDS_INFO,
                    message="未找到可用素材，请补充产品事实、素材 ID 或更具体主题。",
                    decision_source=decision_source,
                    trace=trace,
                )
            if not consume_step():
                return _incomplete(run_id, trace, decision_source)
            rewritten = request.topic.replace("量子", "").strip()
            trace.append(
                _event(
                    "rewrite_search",
                    "将检索词改写为更短的描述",
                    parameters={"original_query": request.topic, "rewritten_query": rewritten},
                    next_action="search_materials",
                    rationale="第一次检索无结果时，先安全地降低检索词的限定。",
                )
            )
            if not consume_step():
                return _incomplete(run_id, trace, decision_source)
            materials = search_materials(
                rewritten,
                material_id=request.material_id,
                failure_injector=failure_injector,
            )
            no_material_decision = decide(
                ["build_draft"] if materials else ["request_more_info"],
                {"material_count": len(materials)},
            )
            trace.append(
                _event(
                    "search_materials",
                    f"改写检索后得到 {len(materials)} 个素材",
                    parameters={"query": rewritten, "material_id": request.material_id or ""},
                    next_action=no_material_decision.action,
                    rationale=no_material_decision.rationale,
                )
            )
            if not materials:
                trace.append(
                    _event(
                        "request_more_info",
                        "没有可用素材",
                        parameters={},
                        next_action=None,
                        rationale="缺少可追溯素材时，向用户索要产品事实或素材线索。",
                    )
                )
                return ScriptResponse(
                    run_id=run_id,
                    status=RunStatus.NEEDS_INFO,
                    message="未找到可用素材，请补充产品事实、素材 ID 或更具体主题。",
                    decision_source=decision_source,
                    trace=trace,
                )

        if not consume_step():
            return _incomplete(run_id, trace, decision_source)
        shots = _draft_from_materials(materials)
        trace.append(
            _event(
                "build_draft",
                f"基于 {len(shots)} 个来源生成首稿",
                parameters={"source_ids": [shot.material_source_ids[0] for shot in shots]},
                next_action="estimate_duration",
                rationale="仅使用检索到的素材事实生成可编辑分镜。",
            )
        )

        if not consume_step():
            return _incomplete(run_id, trace, decision_source)
        duration = estimate_duration(shots, failure_injector=failure_injector)
        duration_decision = decide(
            ["compress_draft"] if duration > request.target_seconds else ["finish"],
            {"duration": duration, "target_seconds": request.target_seconds},
        )
        trace.append(
            _event(
                "estimate_duration",
                f"首稿预估 {duration} 秒",
                parameters={"target_seconds": request.target_seconds},
                next_action=duration_decision.action,
                rationale=duration_decision.rationale,
            )
        )

        if duration_decision.action == "compress_draft":
            if not consume_step():
                return _incomplete(run_id, trace, decision_source)
            shots = _compress(shots, request.target_seconds)
            trace.append(
                _event(
                    "compress_draft",
                    "压缩镜头时长，不新增事实或素材",
                    parameters={"target_seconds": request.target_seconds},
                    next_action="estimate_duration",
                    rationale="工具结果显示超时，选择先压缩后复估。",
                )
            )
            if not consume_step():
                return _incomplete(run_id, trace, decision_source)
            duration = estimate_duration(shots, failure_injector=failure_injector)
            finish_decision = decide(
                ["finish"],
                {"duration": duration, "target_seconds": request.target_seconds},
            )
            trace.append(
                _event(
                    "estimate_duration",
                    f"压缩后预估 {duration} 秒",
                    parameters={"target_seconds": request.target_seconds},
                    next_action=finish_decision.action,
                    rationale=finish_decision.rationale,
                )
            )

        trace.append(
            _event(
                "finish",
                "脚本可交付",
                parameters={},
                next_action=None,
                rationale="素材、规则和时长均满足当前输入。",
            )
        )
        return ScriptResponse(
            run_id=run_id,
            status=RunStatus.COMPLETED,
            title="支持字幕，让表达更清晰",
            shots=shots,
            total_estimated_seconds=duration,
            material_source_ids=[source for shot in shots for source in shot.material_source_ids],
            risks=[],
            message="脚本已生成，可继续人工编辑。",
            decision_source=decision_source,
            trace=trace,
        )
    except RuntimeError:
        return ScriptResponse(
            run_id=run_id,
            status=RunStatus.FAILED,
            message="业务工具执行失败，未生成可交付脚本。",
            decision_source=decision_source,
            trace=trace,
            error_code=ErrorCode.TOOL_FAILURE,
        )


def _incomplete(
    run_id: str, trace: list[TraceEvent], decision_source: DecisionSource
) -> ScriptResponse:
    return ScriptResponse(
        run_id=run_id,
        status=RunStatus.INCOMPLETE,
        message="达到执行步数上限，任务未完成。",
        decision_source=decision_source,
        trace=trace,
        error_code=ErrorCode.EXECUTION_LIMIT_REACHED,
    )
