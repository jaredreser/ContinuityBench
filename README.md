# ContinuityBench

ContinuityBench is a benchmark suite for evaluating whether AI systems can preserve, update, resume, fork, and recombine task state across multi-turn interactions.

Most benchmarks score isolated answers. ContinuityBench scores behavioral continuity: whether a model carries the right state forward, drops stale facts, resumes interrupted work, and branches cleanly when assumptions change.

## MVP

This repository currently contains a small dependency-free Python harness:

- JSON task definitions
- a CLI runner
- deterministic scoring for public state summaries
- example tasks for state updates, interruption recovery, and midpoint forking
- a mock adapter for validating the harness without calling a model API

## Run

```bash
python -m continuitybench run --suite tasks/mvp.json --adapter mock --out runs/mock-mvp.json
```

Print the report to stdout:

```bash
python -m continuitybench run --suite tasks/mvp.json --adapter mock
```

## Task Format

Each task is a multi-turn interaction with an expected final public state:

```json
{
  "id": "kitchen_robot_state_update_001",
  "family": "state_update",
  "turns": [
    {
      "role": "user",
      "content": "A robot is in a kitchen. The floor is dry. The stove is on. A child is nearby."
    }
  ],
  "expected_state": {
    "retain": ["floor is wet"],
    "discard": ["child is nearby"],
    "answer_should_include": ["move carefully"]
  }
}
```

Systems under test should return JSON with these fields when possible:

```json
{
  "active_objective": "...",
  "active_facts": [],
  "discarded_facts": [],
  "current_plan": [],
  "unresolved_questions": [],
  "answer": "..."
}
```

The benchmark does not require private chain-of-thought. It evaluates the public task state and final answer.
