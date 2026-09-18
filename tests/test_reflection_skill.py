from ai_memory_learning import *
from ai_memory_learning.reflection import Reflector
from ai_memory_learning.skills import SkillLibrary

def test_reflection_is_hypothesis():
    from datetime import datetime,timezone
    e=Experience('e',datetime.now(timezone.utc),'c','g','a','x','y',0,'timeout',(),confidence=1)
    r=Reflector().reflect(e)
    assert r.is_hypothesis and r.confidence==.5

def test_skill_requires_verification(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        skill=Skill('s','test','run tests',('run pytest',),regression_tests=('pytest -q',),confidence=.9,verified=False)
        import pytest
        with pytest.raises(ValueError): SkillLibrary(s).promote(skill)
