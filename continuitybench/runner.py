from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Any

from .adapters import ModelAdapter
from .schema import Suite, Task
from .scoring import score_task_report


@dataclass
class TaskResult:
    task_id: str
    family: str
    adapter: str
    raw_response: str
    scores: dict[str, float]
    details: dict[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "family": self.family,
            "adapter": self.adapter,
            "scores": self.scores,
            "details": self.details,
            "raw_response": self.raw_response,
        }


@dataclass
class SuiteReport:
    suite_id: str
    adapter: str
    aggregate_scores: dict[str, float]
    task_results: list[TaskResult]

    def to_dict(self) -> dict[str, Any]:
        return {
            "suite_id": self.suite_id,
            "adapter": self.adapter,
            "aggregate_scores": self.aggregate_scores,
            "task_results": [result.to_dict() for result in self.task_results],
        }


def run_task(task: Task, adapter: ModelAdapter) -> TaskResult:
    raw_response = adapter.complete(task, task.turns)
    report = score_task_report(task, raw_response)
    return TaskResult(
        task_id=task.id,
        family=task.family,
        adapter=adapter.name,
        raw_response=raw_response,
        scores=report["scores"],
        details=report["details"],
    )


def run_suite(suite: Suite, adapter: ModelAdapter) -> SuiteReport:
    task_results = [run_task(task, adapter) for task in suite.tasks]
    aggregate_scores = _aggregate_scores(task_results)
    return SuiteReport(
        suite_id=suite.id,
        adapter=adapter.name,
        aggregate_scores=aggregate_scores,
        task_results=task_results,
    )


def _aggregate_scores(results: list[TaskResult]) -> dict[str, float]:
    score_names = sorted({name for result in results for name in result.scores})
    return {
        name: round(mean(result.scores[name] for result in results if name in result.scores), 4)
        for name in score_names
    }
