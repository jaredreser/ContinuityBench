from __future__ import annotations

import json
from typing import Any

from .schema import Task


ScoreDetails = dict[str, list[dict[str, Any]]]


def score_task(task: Task, raw_response: str) -> dict[str, float]:
    return score_task_report(task, raw_response)["scores"]


def score_task_report(task: Task, raw_response: str) -> dict[str, Any]:
    response = _parse_response(raw_response)
    active_text = _field_text(response, ["active_facts", "current_plan", "answer"])
    discarded_text = _field_text(response, ["discarded_facts"])
    all_text = _normalize(raw_response)

    retention_items = _item_matches(task.expected_state.retain, active_text)
    eviction_items = _item_matches(task.expected_state.discard, discarded_text)
    answer_items = _item_matches(task.expected_state.answer_should_include, all_text)
    stale_items = _item_matches(task.expected_state.discard, active_text)

    retention = _coverage(retention_items)
    eviction = _coverage(eviction_items)
    answer = _coverage(answer_items)
    stale_penalty = _coverage(stale_items)

    continuity = (retention + eviction + answer + (1.0 - stale_penalty)) / 4

    scores = {
        "continuity": round(continuity, 4),
        "relevant_retention": round(retention, 4),
        "irrelevance_eviction": round(eviction, 4),
        "answer_coverage": round(answer, 4),
        "stale_context_penalty": round(stale_penalty, 4),
    }

    scores.update(_family_scores(task.family, scores))

    return {
        "scores": scores,
        "details": {
            "retain": retention_items,
            "discard": eviction_items,
            "answer_should_include": answer_items,
            "stale_context": stale_items,
        },
    }


def _parse_response(raw_response: str) -> dict[str, Any]:
    try:
        parsed = json.loads(raw_response)
    except json.JSONDecodeError:
        return {"answer": raw_response}

    if isinstance(parsed, dict):
        return parsed
    return {"answer": raw_response}


def _field_text(response: dict[str, Any], fields: list[str]) -> str:
    values = [response.get(field, "") for field in fields]
    return _normalize(" ".join(_stringify(value) for value in values))


def _stringify(value: Any) -> str:
    if isinstance(value, list):
        return " ".join(_stringify(item) for item in value)
    if isinstance(value, dict):
        return " ".join(_stringify(item) for item in value.values())
    return str(value)


def _family_scores(family: str, scores: dict[str, float]) -> dict[str, float]:
    if family == "state_update":
        return {
            "state_update_quality": round(
                (
                    scores["relevant_retention"]
                    + scores["irrelevance_eviction"]
                    + (1.0 - scores["stale_context_penalty"])
                )
                / 3,
                4,
            )
        }
    if family == "interruption_recovery":
        return {
            "thread_rehydration": round(
                (scores["relevant_retention"] + scores["answer_coverage"]) / 2,
                4,
            )
        }
    if family == "midpoint_forking":
        return {
            "branch_purity": round(
                (scores["irrelevance_eviction"] + (1.0 - scores["stale_context_penalty"])) / 2,
                4,
            )
        }
    if family == "subsolution_braiding":
        return {
            "subsolution_merge": round(
                (scores["relevant_retention"] + scores["answer_coverage"]) / 2,
                4,
            )
        }
    return {}


def _item_matches(expected_items: list[str], observed_text: str) -> list[dict[str, Any]]:
    return [
        {"item": item, "matched": _normalize(item) in observed_text}
        for item in expected_items
    ]


def _coverage(items: list[dict[str, Any]]) -> float:
    if not items:
        return 1.0
    matches = sum(1 for item in items if item["matched"])
    return matches / len(items)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())
