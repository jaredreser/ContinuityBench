from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Turn:
    role: str
    content: str


@dataclass(frozen=True)
class ExpectedState:
    retain: list[str]
    discard: list[str]
    answer_should_include: list[str]


@dataclass(frozen=True)
class Task:
    id: str
    family: str
    turns: list[Turn]
    expected_state: ExpectedState
    objective: str | None = None


@dataclass(frozen=True)
class Suite:
    id: str
    tasks: list[Task]


def load_suite(path: Path) -> Suite:
    data = json.loads(path.read_text(encoding="utf-8"))
    return parse_suite(data)


def parse_suite(data: dict[str, Any]) -> Suite:
    return Suite(
        id=data["id"],
        tasks=[parse_task(task) for task in data["tasks"]],
    )


def parse_task(data: dict[str, Any]) -> Task:
    expected = data["expected_state"]
    return Task(
        id=data["id"],
        family=data["family"],
        objective=data.get("objective"),
        turns=[Turn(role=turn["role"], content=turn["content"]) for turn in data["turns"]],
        expected_state=ExpectedState(
            retain=list(expected.get("retain", [])),
            discard=list(expected.get("discard", [])),
            answer_should_include=list(expected.get("answer_should_include", [])),
        ),
    )
