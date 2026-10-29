from __future__ import annotations

from ..models import Shot
from .failure_injection import FailureInjector


def estimate_duration(
    shots: list[Shot], *, failure_injector: FailureInjector | None = None
) -> int:
    if failure_injector:
        failure_injector.check("estimate_duration")
    return sum(shot.estimated_seconds for shot in shots)

