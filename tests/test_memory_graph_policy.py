from datetime import datetime, timezone
from ai_memory_learning.models import MessageRecord
from ai_memory_learning.memory import MemoryFact
from ai_memory_learning.graph import Relationship, RelationshipGraph
from ai_memory_learning.policy import RetrievalPolicy
from ai_memory_learning.retrieval import Retriever
from ai_memory_learning.store import SQLiteStore

def test_structured_memory_and_graph(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_fact(MemoryFact('f1','agent','uses','external-memory',('src-1',),.95))
        assert s.get_fact('f1').value == 'external-memory'
        RelationshipGraph(s).add(Relationship('r1','agent','uses','memory',('src-1',),.9))
        assert s.neighbors('agent')[0].object_id == 'memory'

def test_retrieval_policy_can_withhold_messages(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_message(MessageRecord('m1','c',1,'user','secret evidence',datetime.now(timezone.utc)))
        hits=Retriever(s,RetrievalPolicy(allow_messages=False)).search('secret evidence')
        assert all(h.kind != 'message' for h in hits)
