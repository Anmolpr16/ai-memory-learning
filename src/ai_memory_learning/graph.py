from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Relationship:
    relationship_id: str
    subject_id: str
    predicate: str
    object_id: str
    source_ids: tuple[str, ...] = ()
    confidence: float = 0.0

class RelationshipGraph:
    def __init__(self, store): self.store = store
    def add(self, relationship): self.store.add_relationship(relationship)
    def neighbors(self, entity_id): return self.store.neighbors(entity_id)
