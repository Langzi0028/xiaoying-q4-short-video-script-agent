from __future__ import annotations

import json
import sys
from pathlib import Path

import typer

from .fixtures.scenarios import p01_request, unmatched_request
from .config import Settings
from .graph.workflow import run_request
from .llm.client import LiveDecisionEngine
from .models import ScriptRequest
from .storage.repositories import RunRepository
from .tools.failure_injection import FailureInjector


app = typer.Typer(no_args_is_help=True)


def _decision_engine():
    settings = Settings.from_environment()
    if not settings.llm_configured:
        print("LLM configuration missing; using deterministic fallback.", file=sys.stderr)
        return None
    return LiveDecisionEngine(settings)


def _emit(response, database: Path) -> None:
    repository = RunRepository(database)
    try:
        repository.save(response)
    finally:
        repository.close()
    typer.echo(response.model_dump_json(), nl=True)


def _announce_llm_failure(error: BaseException) -> None:
    print(
        f"LLM request failed: {type(error).__name__}; using deterministic fallback.",
        file=sys.stderr,
    )


@app.command()
def run(
    topic: str = typer.Option(..., "--topic"),
    audience: str = typer.Option(..., "--audience"),
    target_seconds: int = typer.Option(..., "--target-seconds"),
    style: str = typer.Option(..., "--style"),
    material_id: str | None = typer.Option(None, "--material-id"),
    product_fact: list[str] = typer.Option([], "--product-fact"),
    brand_rule: list[str] = typer.Option([], "--brand-rule"),
    max_steps: int = typer.Option(24, "--max-steps", min=1),
    database: Path = typer.Option(Path("data/script_agent.db"), "--database"),
) -> None:
    response = run_request(
        ScriptRequest(
            topic=topic,
            audience=audience,
            target_seconds=target_seconds,
            style=style,
            material_id=material_id,
            product_facts=product_fact,
            brand_rules=brand_rule,
        ),
        max_steps=max_steps,
        decision_engine=_decision_engine(),
        on_llm_failure=_announce_llm_failure,
    )
    _emit(response, database)


@app.command()
def demo(
    scenario: str = typer.Argument(...),
    database: Path = typer.Option(Path("data/demo_script_agent.db"), "--database"),
) -> None:
    engine = _decision_engine()
    if scenario == "p01-overlength":
        response = run_request(p01_request(target_seconds=30), decision_engine=engine, on_llm_failure=_announce_llm_failure)
    elif scenario == "no-material":
        response = run_request(unmatched_request(), decision_engine=engine, on_llm_failure=_announce_llm_failure)
    elif scenario == "rule-risk":
        response = run_request(p01_request(topic="绝对保证治愈", target_seconds=30), decision_engine=engine, on_llm_failure=_announce_llm_failure)
    elif scenario == "tool-failure":
        response = run_request(
            p01_request(target_seconds=30),
            failure_injector=FailureInjector(fail_actions={"estimate_duration"}),
            decision_engine=engine,
            on_llm_failure=_announce_llm_failure,
        )
    elif scenario == "execution-limit":
        response = run_request(p01_request(target_seconds=30), max_steps=1, decision_engine=engine, on_llm_failure=_announce_llm_failure)
    else:
        raise typer.BadParameter("scenario must be p01-overlength, no-material, rule-risk, tool-failure, or execution-limit")
    _emit(response, database)


@app.command()
def show(
    run_id: str = typer.Option(..., "--run-id"),
    database: Path = typer.Option(Path("data/script_agent.db"), "--database"),
) -> None:
    repository = RunRepository(database)
    try:
        response = repository.get(run_id)
    finally:
        repository.close()
    if response is None:
        raise typer.BadParameter("run_id not found")
    typer.echo(json.dumps(response.model_dump(mode="json"), ensure_ascii=False))


def main() -> None:
    app()
