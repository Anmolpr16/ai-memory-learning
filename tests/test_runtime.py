from datetime import datetime,timezone
from ai_memory_learning import *
def test_verified_experience_updates_lesson(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_lesson(Lesson('l','run tests','run pytest','pass','pass',0,.2))
        e=Experience('e',datetime.now(timezone.utc),'ctx','test','run pytest','pass','pass',1,None,(EvidenceRef('src'),),confidence=.9)
        ev,res=MemoryLearningRuntime(s).run(e,'l')
        assert ev.status=='pass' and res.evidence_count==1
        assert s.get_experience('e').verification_status=='verified'
def test_unverified_cannot_learn(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_lesson(Lesson('l','x','y','z','z',0,.2))
        e=Experience('e',datetime.now(timezone.utc),'c','g','a','expected','unknown',0,None,(),confidence=.5)
        s.add_experience(e)
        import pytest
        with pytest.raises(ValueError):
            from ai_memory_learning.learning import LearningEngine
            LearningEngine(s).learn_from_verified_experience('e','l')
