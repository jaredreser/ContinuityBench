# Benchmark Design

ContinuityBench evaluates whether an AI system can maintain an evolving public task state across turns. It is not a chain-of-thought benchmark. The system under test can answer directly, but it is encouraged to expose a compact state summary that can be scored.

## What Counts as Continuity

Continuity means the system can:

- preserve facts that remain relevant
- discard facts that have become stale
- update a plan when the world changes
- resume a task after interruption
- fork from an earlier assumption without contaminating the new branch
- combine partial results from separate threads

## Public State Contract

The preferred response shape is:

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

This contract is intentionally small. It gives the scorer observable state without asking the model to reveal private reasoning.

## MVP Task Families

`state_update` tests whether a model can keep a current state after facts change.

`interruption_recovery` tests whether a model can resume the original thread after an unrelated turn.

`midpoint_forking` tests whether a model can replace an earlier assumption and avoid importing conclusions from the abandoned branch.

`subsolution_braiding` tests whether a model can preserve separate partial findings and synthesize them into a better combined answer.

## Scoring Philosophy

The first scorer is deterministic and transparent. Each expected item is checked against the model's public state and answer. This is intentionally simple enough to audit.

Future scorers should add semantic matching, adversarial paraphrases, calibrated LLM-as-judge evaluation, and task generators. The deterministic scorer should remain as the baseline because it makes benchmark failures easy to inspect.
