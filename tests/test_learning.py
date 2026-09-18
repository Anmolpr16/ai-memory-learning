from datetime import datetime, timezone
import pytest
from ai_memory_learning import *
from ai_memory_learning.learning import LearningEngine
def test_unverified_experience_cannot_update_lesson(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_lesson(Lesson('l1','python test','run tests','verified result','tests pass',0,.2))
        e=Experience('e1',datetime.now(timezone.utc),'ctx','goal','run tests','pass','pass',1,None,(EvidenceRef('src1'),),'unverified',1)
        s.add_experience(e)
        with pytest.raises(ValueError): LearningEngine(s).learn_from_verified_experience('e1','l1')
