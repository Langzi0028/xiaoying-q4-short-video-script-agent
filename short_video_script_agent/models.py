from __future__ import annotations

from pydantic import BaseModel, Field, field_validator

from .enums import DecisionSource, ErrorCode, RunStatus


class ScriptRequest(BaseModel):
    topic: str = Field(min_length=1)
    audience: str = Field(min_length=1)
    target_seconds: int = Field(gt=0, le=180)
    style: str = Field(min_length=1)
    material_id: str | None = None
    product_facts: list[str] = Field(default_factory=list)
    brand_rules: list[str] = Field(default_factory=list)

    @field_validator("topic", "audience", "style", "material_id")
    @classmethod
    def strip_strings(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class Material(BaseModel):
    source_id: str
    product_id: str
    title: str
    keywords: list[str]
    fact: str
    visual: str
    duration_seconds: int = Field(gt=0)


class Shot(BaseModel):
    index: int = Field(gt=0)
    visual_description: str
    voiceover: str
    subtitle: str
    estimated_seconds: int = Field(gt=0)
    material_source_ids: list[str]


class TraceEvent(BaseModel):
    node: str
    action: str
    parameters: dict[str, object] = Field(default_factory=dict)
    result_summary: str
    next_action: str | None = None
    decision_rationale: str

    def __getitem__(self, key: str) -> object:
        return getattr(self, key)

    def __iter__(self):
        return iter(self.model_dump())


class ScriptResponse(BaseModel):
    run_id: str
    status: RunStatus
    title: str | None = None
    shots: list[Shot] = Field(default_factory=list)
    total_estimated_seconds: int = 0
    material_source_ids: list[str] = Field(default_factory=list)
    risks: list[str] = Field(default_factory=list)
    message: str = ""
    decision_source: DecisionSource
    trace: list[TraceEvent] = Field(default_factory=list)
    error_code: ErrorCode | None = None
