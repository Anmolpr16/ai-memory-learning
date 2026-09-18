from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Reflection:
    experience_id:str; diagnosis:str; lesson_candidate:str; confidence:float; is_hypothesis:bool=True

class Reflector:
    """Generates hypotheses only; verification remains external to reflection."""
    def reflect(self,experience):
        if experience.failure_type: diagnosis=f"Observed failure type: {experience.failure_type}. Compare action, goal, prediction, and environment before changing policy."
        elif experience.prediction.strip().lower()==experience.outcome.strip().lower(): diagnosis="Prediction matched observed outcome."
        else: diagnosis="Prediction and outcome differ; causal explanation requires independent evidence."
        return Reflection(experience.experience_id,diagnosis,"Treat the pattern as a hypothesis until independently verified.",max(0,min(1,experience.confidence*.5)))
