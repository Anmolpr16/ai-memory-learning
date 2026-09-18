from __future__ import annotations
from dataclasses import dataclass
from .models import MessageRecord, Lesson

@dataclass(frozen=True)
class MemoryFact:
    fact_id: str
    subject: str
    predicate: str
    value: str
    source_ids: tuple[str, ...]
    confidence: float = 0.0
    valid_from: str | None = None
    valid_to: str | None = None

class FactStore:
    """Structured semantic memory facade backed by SQLiteStore."""
    def __init__(self, store): self.store = store
    def add(self, fact: MemoryFact):
        self.store.add_fact(fact)
    def get(self, fact_id):
        return self.store.get_fact(fact_id)
    def search(self, subject=None, predicate=None):
        return self.store.search_facts(subject, predicate)
