from __future__ import annotations
import re
from dataclasses import dataclass
from .policy import RetrievalPolicy, AccessDenied

@dataclass(frozen=True)
class RetrievalHit:
    kind: str; record_id: str; score: float; reason: str

def _tokens(s): return {x.lower() for x in re.findall(r"\b\w+\b", s)}

class Retriever:
    """Deterministic hybrid-ready retriever: lexical FTS + structured metadata/confidence."""
    def __init__(self, store, policy=None): self.store=store; self.policy=policy or RetrievalPolicy()
    def search(self, query, limit=10):
        limit=min(max(1,limit), self.policy.max_results); q=_tokens(query); hits=[]
        if self.policy.permits("message"):
            for m in self.store.search_messages(query, limit*3):
                overlap=len(q&_tokens(m.content)); hits.append(RetrievalHit("message",m.message_id,float(overlap)+1.0,"lexical + FTS"))
        if self.policy.permits("lesson"):
            for l in self.store.iter_lessons():
                text=" ".join((l.condition,l.action,l.expected_effect,l.observed_effect,*l.exceptions)); overlap=len(q&_tokens(text))
                if overlap: hits.append(RetrievalHit("lesson",l.lesson_id,float(overlap)+l.confidence,"lexical + confidence"))
        if self.policy.permits("experience"):
            for e in self.store.iter_experiences():
                text=" ".join((e.goal,e.action,e.prediction,e.outcome,e.failure_type or "")); overlap=len(q&_tokens(text))
                if overlap: hits.append(RetrievalHit("experience",e.experience_id,float(overlap)+e.confidence,"lexical + confidence"))
        return sorted(hits,key=lambda h:(-h.score,h.kind,h.record_id))[:limit]

HybridRetriever=Retriever
