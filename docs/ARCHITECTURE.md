# Architecture v1.0

## 1. Evidence plane

Canonical messages are the source of truth. Each message contains stable identity, conversation ordering, timestamp, role, schema version, parent/edit lineage, and a deterministic SHA-256 content hash.

The SQLite store is a local durable implementation. The append-only JSONL archive remains available as a simple portable projection.

## 2. Retrieval plane

FTS5 supplies deterministic lexical retrieval. The `HybridRetriever` API is intentionally provider/index neutral. Future semantic embeddings, time filters, entities, continuity, reranking, and contradiction risk should be added as renewable projections rather than replacing canonical records.

## 3. Experience plane

An experience records context, goal, action, prediction, outcome, reward, failure type, evidence, verification status, and confidence. Evidence is stored separately and linked by source IDs/message IDs.

## 4. Evaluation plane

`OutcomeEvaluator` is deliberately conservative. It can verify simple deterministic outcomes, but it does not claim that model reflection is proof. Production evaluators should include tests, exact checkers, simulators, external feedback, or specialized evaluators appropriate to the task.

## 5. Learning plane

Only verified experiences may update lessons. Contradictions are attached instead of silently replacing prior evidence. Confidence is evidence-accumulating rather than an unconditional overwrite.

## 6. Event plane

The runtime emits `act`, `observe`, `evaluate`, and `update` events. Events are append-only records with hashes and schema versions, providing an auditable execution history.

## 7. Skill plane

Skills are explicit reusable procedures with preconditions, regression tests, confidence, and verification state. A later skill extractor must require repeatable verified evidence before promoting an experience into a skill.

## 8. Century-scale deployment boundary

A production archival deployment must add independent replicas/failure domains, immutable backups, periodic fixity scans, restore tests, open/versioned export formats, migration procedures, encryption/key recovery, audit logs, deletion/export policy, and rebuildable search/vector indexes. The research explicitly treats these as infrastructure around the replaceable AI rather than properties of model weights.


## 9. Structured memory and graph

Facts provide explicit subject/predicate/value records with source IDs and confidence. Relationships provide a small provenance-aware graph. Both are derived/structured memory, not substitutes for the canonical archive.

## 10. Retrieval policy

Retrieval is policy-gated. A record can exist durably while policy prevents a given agent from surfacing it. This separates preservation from authorization.

## 11. Verification and learning boundary

The runtime records an experience, evaluates its observed result, creates a reflection hypothesis, and only then permits a verified experience to update a lesson. Skills require explicit verification and a confidence threshold before promotion.
