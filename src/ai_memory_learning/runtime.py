from __future__ import annotations
import uuid
from .models import Event, utc_now
from .evaluation import OutcomeEvaluator
from .learning import LearningEngine
from .reflection import Reflector

class MemoryLearningRuntime:
    """Auditable ACT -> OBSERVE -> EVALUATE -> REFLECT -> UPDATE runtime."""
    def __init__(self,store,evaluator=None,reflector=None):
        self.store=store; self.evaluator=evaluator or OutcomeEvaluator(); self.reflector=reflector or Reflector(); self.learning=LearningEngine(store)
    def emit(self,event_type,payload):
        e=Event(str(uuid.uuid4()),event_type,utc_now(),payload); self.store.add_event(e); return e
    def run(self,experience,lesson_id=None):
        self.emit('act',{'experience_id':experience.experience_id,'action':experience.action})
        self.store.add_experience(experience)
        self.emit('observe',{'experience_id':experience.experience_id,'outcome':experience.outcome})
        evaluation=self.evaluator.evaluate(experience); self.store.add_evaluation(evaluation)
        self.emit('evaluate',{'experience_id':experience.experience_id,'status':evaluation.status,'score':evaluation.score})
        reflection=self.reflector.reflect(experience)
        self.emit('reflect',{'experience_id':experience.experience_id,'diagnosis':reflection.diagnosis,'hypothesis':reflection.is_hypothesis})
        result=None
        if lesson_id:
            result=self.learning.verify_and_learn(experience.experience_id,lesson_id,evaluation)
            self.emit('update',{'experience_id':experience.experience_id,'lesson_id':lesson_id,'verified':evaluation.status=='pass'})
        return evaluation,result
