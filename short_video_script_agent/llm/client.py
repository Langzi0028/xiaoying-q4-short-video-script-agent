from __future__ import annotations

from langchain_openai import ChatOpenAI
import json

from ..config import Settings
from ..enums import DecisionSource
from .decision_tools import Decision, validate_decision


class LiveDecisionEngine:
    """Make a constrained online action selection without logging prompt contents."""

    def __init__(self, settings: Settings) -> None:
        self.client = ChatOpenAI(
            api_key=settings.api_key,
            base_url=settings.base_url,
            model=settings.model,
            temperature=0,
        )

    def choose(self, legal_actions: list[str], state: dict[str, object]) -> Decision:
        safe_state = {key: state[key] for key in ("duration", "target_seconds", "material_count") if key in state}
        response = self.client.invoke(
            [
                (
                    "system",
                    "Choose exactly one action from the legal list. Return JSON with action and rationale only.",
                ),
                (
                    "user",
                    f"legal_actions={legal_actions}; safe_state={safe_state}",
                ),
            ]
        )
        if isinstance(response.content, dict):
            parsed = response.content
        else:
            try:
                parsed = json.loads(str(response.content))
            except json.JSONDecodeError:
                parsed = {}
        decision = Decision(
            action=str(parsed.get("action", "")),
            rationale=str(parsed.get("rationale", "")),
            source=DecisionSource.LIVE_LLM,
        )
        return validate_decision(
            decision,
            legal_actions=legal_actions,
            fallback_action=legal_actions[0],
        )
