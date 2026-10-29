from __future__ import annotations

from ..fixtures.scenarios import MATERIALS
from ..models import Material
from .failure_injection import FailureInjector


def search_materials(
    query: str,
    *,
    material_id: str | None = None,
    failure_injector: FailureInjector | None = None,
) -> list[Material]:
    if failure_injector:
        failure_injector.check("search_materials")
    query_terms = set(query.lower().replace("，", " ").split())
    matched: list[Material] = []
    for material in MATERIALS:
        if material_id and material.product_id != material_id:
            continue
        searchable = " ".join([material.title, material.fact, *material.keywords]).lower()
        if any(term in searchable for term in query_terms) or (material_id and "字幕" in query):
            matched.append(material)
    return matched

