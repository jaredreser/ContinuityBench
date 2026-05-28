import json

from continuitybench.schema import ExpectedState, Task
from continuitybench.scoring import score_task, score_task_report


def test_score_task_detects_retention_eviction_and_stale_context():
    task = Task(
        id="example",
        family="state_update",
        turns=[],
        expected_state=ExpectedState(
            retain=["floor is wet"],
            discard=["child is nearby"],
            answer_should_include=["move carefully"],
        ),
    )
    response = json.dumps(
        {
            "active_facts": ["floor is wet"],
            "discarded_facts": ["child is nearby"],
            "answer": "The robot should move carefully.",
        }
    )

    scores = score_task(task, response)

    assert scores["relevant_retention"] == 1.0
    assert scores["irrelevance_eviction"] == 1.0
    assert scores["answer_coverage"] == 1.0
    assert scores["stale_context_penalty"] == 0.0
    assert scores["continuity"] == 1.0


def test_score_task_report_includes_item_level_details():
    task = Task(
        id="example",
        family="midpoint_forking",
        turns=[],
        expected_state=ExpectedState(
            retain=["new assumption"],
            discard=["old assumption"],
            answer_should_include=["revised conclusion"],
        ),
    )
    response = json.dumps(
        {
            "active_facts": ["new assumption"],
            "discarded_facts": ["old assumption"],
            "answer": "The revised conclusion follows.",
        }
    )

    report = score_task_report(task, response)

    assert report["scores"]["branch_purity"] == 1.0
    assert report["details"]["retain"] == [{"item": "new assumption", "matched": True}]
    assert report["details"]["discard"] == [{"item": "old assumption", "matched": True}]
