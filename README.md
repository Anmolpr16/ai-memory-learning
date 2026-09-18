# AI Memory & Experiential Learning

A research-grounded implementation of durable external AI memory and evidence-based experiential learning.

## Core invariant

**Archive truth is separate from AI state.** Raw records are canonical; indexes, summaries, embeddings, lessons, and skills are derived and renewable.

## Runtime

```text
INPUT
  ↓
CANONICAL ARCHIVE → INTEGRITY / PROVENANCE
  ↓
RETRIEVE → PLAN / ACT → OBSERVE → EVALUATE
                         ↓
                      REFLECT
                         ↓
                 LESSON / SKILL UPDATE
                         ↓
                      RETRIEVE
```

The implementation includes:

- immutable-style canonical message records with SHA-256 fixity hashes;
- SQLite durable local store with WAL and FTS5 lexical search;
- provenance-linked experiences and evidence;
- deterministic outcome evaluation;
- controlled verification before lesson updates;
- contradiction preservation;
- event log for runtime state transitions;
- skills and regression-test data model;
- JSONL export and integrity manifest;
- deterministic hybrid retrieval boundary ready for semantic/vector projections;
- CLI, local HTTP API, dependency-free OpenAI-compatible provider adapter, and automated tests.

## Quick start

```bash
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest -q
aimemory init memory.db
aimemory message memory.db m1 c1 'durable memory example'
aimemory search memory.db durable
aimemory serve memory.db --host 127.0.0.1 --port 8787
```

## Design principles

1. Preserve original evidence; never make a generated summary the only copy.
2. Treat indexes and embeddings as renewable projections.
3. Require provenance for structured memory and lessons.
4. Treat reflection as a hypothesis and independent evaluation as the verification boundary.
5. Preserve contradictory evidence instead of silently overwriting it.
6. Allow the model, embedding model, and retrieval implementation to be replaced independently.
7. Separate authorization policy from the existence of stored memory.

## Model integration

The core does not require a specific model. An optional dependency-free OpenAI-compatible adapter can be configured with `AI_MEMORY_BASE_URL`, `AI_MEMORY_MODEL`, and optionally `AI_MEMORY_API_KEY`. The local HTTP API exposes `/health`, `/messages`, and `/search` for Android, IDE, or other clients.

## Production boundary

The local runtime is complete as a reference/MVP core, but century-scale preservation requires deployment-specific independent replicas, geographic separation, tested restores, migration planning, durable key management, access-control policy, and object/archive tiers. Those cannot honestly be reduced to a local SQLite feature.
