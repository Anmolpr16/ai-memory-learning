from datetime import datetime, timezone

from ai_memory_learning.models import MemoryStore, MessageRecord, Lesson
from ai_memory_learning.retrieval import Retriever


def test_retrieval_returns_lexical_matches():
    store = MemoryStore()
    store.add_message(MessageRecord("m1", "c", 1, "user", "verified memory retrieval", datetime.now(timezone.utc)))
    store.add_lesson(Lesson("l1", "memory", "retrieve evidence", "grounded answer", "verified", 1, 0.9))
    hits = Retriever(store).search("memory evidence")
    assert hits
    assert {h.record_id for h in hits} == {"m1", "l1"}
