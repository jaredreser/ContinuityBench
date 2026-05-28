from __future__ import annotations

import json
from typing import Any

from .schema import Task


def score_task(task: Task, raw_response: str) -> dict[str, float]:
    response = _parse_response(raw_response)
    active_text = _field_text(response, ["active_facts", "current_plan", "answer"])
    discarded_text = _field_text(response, ["discarded_facts"])
    all_text = _normalize(raw_response)

    retention = _coverage(task.expected_state.retain, active_text)
    eviction = _coverage(task.expected_state.discard, discarded_text)
    answer = _coverage(task.expected_state.answer_should_include, all_text)
    stale_penalty = _coverage(task.expected_state.discard, active_text)

    continuity = (retention + eviction + answer + (1.0 - stale_penalty)) / 4

    return {
        "continuity": round(continuity, 4),
        "relevant_retention": round(retention, 4),
        "irrelevance_eviction": round(eviction, 4),
        "answer_coverage": round(answer, 4),
        "stale_context_penalty": round(stale_penalty, 4),
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


def _coverage(expected_items: list[str], observed_text: str) -> float:
    if not expected_items:
        return 1.0
    matches = sum(1 for item in expected_items if _normalize(item) in observed_text)
    return matches / len(expected_items)


def _normalize(text: str) -> str:
    return " ".join(text.casefold().split())
