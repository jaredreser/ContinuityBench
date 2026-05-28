from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Protocol

from .schema import Task, Turn


class ModelAdapter(Protocol):
    name: str

    def complete(self, task: Task, turns: list[Turn]) -> str:
        """Return the model response for a task transcript."""


@dataclass
class MockAdapter:
    """A deterministic adapter that echoes expected state for harness testing."""

    name: str = "mock"

    def complete(self, task: Task, turns: list[Turn]) -> str:
        expected = task.expected_state
        response = {
            "active_objective": task.objective or f"Complete {task.family} task",
            "active_facts": expected.retain,
            "discarded_facts": expected.discard,
            "current_plan": expected.answer_should_include,
            "unresolved_questions": [],
            "answer": " ".join(expected.answer_should_include),
        }
        return json.dumps(response, indent=2)


def get_adapter(name: str) -> ModelAdapter:
    if name == "mock":
        return MockAdapter()
    raise ValueError(f"Unknown adapter: {name}")
