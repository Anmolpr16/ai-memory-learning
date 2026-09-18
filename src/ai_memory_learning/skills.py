from __future__ import annotations
from dataclasses import dataclass
from .models import Skill

class SkillLibrary:
    def __init__(self,store): self.store=store
    def add(self,skill): self.store.add_skill(skill)
    def promote(self,skill):
        if not skill.verified: raise ValueError("skill must be verified before promotion")
        if skill.confidence<0.8: raise ValueError("skill confidence below promotion threshold")
        self.store.add_skill(skill); return skill

@dataclass(frozen=True)
class SkillTestResult:
    name:str; passed:bool; detail:str=""

class SkillVerifier:
    def verify(self, skill:Skill, checks):
        results=[]
        for name,check in checks:
            try: results.append(SkillTestResult(name,bool(check(skill)),""))
            except Exception as exc: results.append(SkillTestResult(name,False,str(exc)))
        return all(x.passed for x in results),tuple(results)
