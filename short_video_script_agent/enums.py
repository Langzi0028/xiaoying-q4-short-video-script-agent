from enum import StrEnum


class RunStatus(StrEnum):
    COMPLETED = "completed"
    NEEDS_INFO = "needs_info"
    BLOCKED = "blocked"
    FAILED = "failed"
    INCOMPLETE = "incomplete"


class DecisionSource(StrEnum):
    LIVE_LLM = "live_llm"
    FALLBACK = "fallback"


class ErrorCode(StrEnum):
    EXECUTION_LIMIT_REACHED = "EXECUTION_LIMIT_REACHED"
    TOOL_FAILURE = "TOOL_FAILURE"

