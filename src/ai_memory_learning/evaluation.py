from __future__ import annotations
from .models import Evaluation

class Evaluator:
    name="base"
    def evaluate(self, experience): raise NotImplementedError

class OutcomeEvaluator(Evaluator):
    name="outcome"
    def evaluate(self,e):
        outcome=e.outcome.strip().lower(); pred=e.prediction.strip().lower()
        passed=outcome in {"success","pass","passed","true","ok"} or (pred and pred==outcome)
        status="pass" if passed else "fail"
        return Evaluation("eval-"+e.experience_id,e.experience_id,status,1.0 if passed else 0.0,self.name,"Deterministic outcome/prediction comparison.",e.evidence)

class CompositeEvaluator(Evaluator):
    """Combines independent evaluators conservatively: any failure fails; otherwise average scores."""
    name="composite"
    def __init__(self, evaluators): self.evaluators=tuple(evaluators)
    def evaluate(self,e):
        results=[x.evaluate(e) for x in self.evaluators]
        status="fail" if any(x.status=="fail" for x in results) else ("inconclusive" if any(x.status=="inconclusive" for x in results) else "pass")
        score=sum(x.score for x in results)/len(results) if results else 0.0
        return Evaluation("eval-composite-"+e.experience_id,e.experience_id,status,score,self.name,"; ".join(x.rationale for x in results),tuple(r for x in results for r in x.evidence))
