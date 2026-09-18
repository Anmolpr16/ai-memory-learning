from __future__ import annotations
from dataclasses import dataclass
from .retrieval import Retriever, RetrievalHit

@dataclass(frozen=True)
class EvidencePacket:
    query: str
    hits: tuple[RetrievalHit,...]
    source_ids: tuple[str,...]

class MemoryController:
    """Builds compact evidence packets rather than exposing the whole archive."""
    def __init__(self, store, policy=None): self.retriever=Retriever(store, policy)
    def build_context(self, query, limit=8):
        hits=tuple(self.retriever.search(query,limit)); return EvidencePacket(query,hits,tuple(h.record_id for h in hits))
