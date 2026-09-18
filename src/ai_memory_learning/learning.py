from __future__ import annotations
from dataclasses import replace
from .models import Experience

class LearningEngine:
    def __init__(self,store): self.store=store
    def learn_from_verified_experience(self, experience_id, lesson_id):
        e=self.store.get_experience(experience_id); l=self.store.get_lesson(lesson_id)
        if not e or not l: raise KeyError("experience or lesson not found")
        if e.verification_status!="verified": raise ValueError("only verified experiences may update a lesson")
        if experience_id in l.source_experience_ids: return l
        n=l.evidence_count+1
        conf=max(0,min(1,l.confidence+(e.confidence-l.confidence)/n))
        updated=replace(l,evidence_count=n,confidence=conf,last_verified=e.timestamp,source_experience_ids=l.source_experience_ids+(experience_id,))
        self.store.update_lesson(updated); return updated
    def verify_and_learn(self, experience_id, lesson_id, evaluation):
        e=self.store.get_experience(experience_id)
        if not e: raise KeyError(experience_id)
        status="verified" if evaluation.status=="pass" else "rejected"
        e=replace(e,verification_status=status,confidence=max(e.confidence,evaluation.score))
        self.store.update_experience(e)
        return self.learn_from_verified_experience(experience_id,lesson_id) if status=="verified" else self.store.get_lesson(lesson_id)
    def record_contradiction(self, experience_id, lesson_id):
        e=self.store.get_experience(experience_id); l=self.store.get_lesson(lesson_id)
        if not e or not l: raise KeyError("experience or lesson not found")
        if experience_id not in l.contradiction_ids: self.store.update_lesson(replace(l,contradiction_ids=l.contradiction_ids+(experience_id,)))
