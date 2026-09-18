# Deployment and Preservation

This document turns the research requirements into an operational boundary. The repository supplies the local reference implementation; a production deployment supplies the failure-domain infrastructure.

## Required layers

1. **Canonical archive** — retain the original message/evidence records as the source of truth.
2. **Hot store** — SQLite is suitable for a single-node reference deployment; production may replace it with a transactional service.
3. **Independent replicas** — maintain copies in separate failure domains rather than treating one database as the archive.
4. **Immutable/versioned backup** — snapshots must be retained independently from the live database.
5. **Fixity verification** — periodically hash and verify snapshots and archived objects.
6. **Restore drills** — regularly restore a copy into an isolated environment and run database integrity checks plus application-level validation.
7. **Renewable indexes** — FTS, vector indexes, summaries, and embeddings are rebuildable projections, never the sole record.
8. **Migration** — plan schema, storage, cryptographic, and embedding-model migrations before an old format becomes unreadable.
9. **Authorization and audit** — access policy is separate from storage; log access and administrative changes.
10. **Key durability** — production encryption keys require an independent, documented lifecycle and recovery process.

## Model boundary

Models are replaceable dependencies. Use the `ModelProvider` protocol and the included OpenAI-compatible adapter, or implement another provider without changing archive or learning semantics.

## HTTP boundary

`aimemory serve memory.db` starts a small local HTTP service. It is intentionally not presented as an internet-facing production API: authentication, TLS, rate limiting, request authorization, and network isolation must be supplied by the deployment.

## 100-year preservation

No local software feature can guarantee zero data loss for a century. The defensible architecture is layered redundancy, independent failure domains, fixity checks, tested restoration, format migration, and documented operational ownership.
