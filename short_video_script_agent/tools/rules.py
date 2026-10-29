from __future__ import annotations

from ..models import ScriptRequest
from .failure_injection import FailureInjector


FORBIDDEN_CLAIMS = ("绝对", "保证", "治愈", "第一")


def check_brand_rules(
    request: ScriptRequest, *, failure_injector: FailureInjector | None = None
) -> list[str]:
    if failure_injector:
        failure_injector.check("check_rules")
    topic_risks = [f"品牌规则不允许使用: {claim}" for claim in FORBIDDEN_CLAIMS if claim in request.topic]
    declared_risks = [f"品牌规则阻断: {rule}" for rule in request.brand_rules if rule.strip()]
    return topic_risks + declared_risks


def check_factual_rules(request: ScriptRequest, materials: list[object]) -> list[str]:
    """Reject user-provided facts that the selected product sources cannot support."""
    if not request.product_facts:
        return []
    available_facts = {getattr(material, "fact", "") for material in materials}
    return [
        f"缺少可验证来源的产品事实: {fact}"
        for fact in request.product_facts
        if fact not in available_facts
    ]
