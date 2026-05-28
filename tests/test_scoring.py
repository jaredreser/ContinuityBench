import json

from continuitybench.schema import ExpectedState, Task
from continuitybench.scoring import score_task


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
