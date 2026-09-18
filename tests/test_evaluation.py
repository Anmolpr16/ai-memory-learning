from datetime import datetime, timezone
from ai_memory_learning.evaluation import CompositeEvaluator, OutcomeEvaluator
from ai_memory_learning.models import Experience

def e(outcome):
    return Experience('e'+outcome,datetime.now(timezone.utc),'c','g','a','success',outcome,None,None,())
def test_composite_evaluator():
    result=CompositeEvaluator([OutcomeEvaluator()]).evaluate(e('success'))
    assert result.status=='pass' and result.score==1.0
