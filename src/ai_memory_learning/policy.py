from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RetrievalPolicy:
    """Controls whether stored evidence may be surfaced to an agent."""
    allow_messages: bool = True
    allow_lessons: bool = True
    allow_experiences: bool = True
    max_results: int = 20

    def permits(self, kind: str) -> bool:
        return {
            "message": self.allow_messages,
            "lesson": self.allow_lessons,
            "experience": self.allow_experiences,
        }.get(kind, False)

class AccessDenied(PermissionError):
    pass
