from __future__ import annotations

from dataclasses import dataclass

from ..enums import DecisionSource


@dataclass(frozen=True)
class Decision:
    action: str
    rationale: str
    source: DecisionSource


class FallbackDecisionEngine:
    """Choose only from business-code-provided legal actions."""

    def choose(self, legal_actions: list[str], state: dict[str, object]) -> Decision:
        duration = state.get("duration")
        target_seconds = state.get("target_seconds")
        if (
            isinstance(duration, int)
            and isinstance(target_seconds, int)
            and duration > target_seconds
            and "compress_draft" in legal_actions
        ):
            return Decision(
                action="compress_draft",
                rationale="工具估算显示首稿超出目标时长，先压缩后复估。",
                source=DecisionSource.FALLBACK,
            )
        if "finish" in legal_actions:
            return Decision(
                action="finish",
                rationale="当前工具结果已满足完成条件。",
                source=DecisionSource.FALLBACK,
            )
        return Decision(
            action=legal_actions[0],
            rationale="选择确定性安全动作。",
            source=DecisionSource.FALLBACK,
        )


def validate_decision(
    decision: Decision, *, legal_actions: list[str], fallback_action: str
) -> Decision:
    if decision.action in legal_actions:
        return decision
    return Decision(
        action=fallback_action,
        rationale="模型返回了不在合法动作集合中的动作，已使用安全 fallback。",
        source=DecisionSource.FALLBACK,
    )

