"""Durable external AI memory and evidence-based experiential learning."""
__version__='1.0.0'
from .models import MessageRecord, EvidenceRef, Experience, Lesson, Skill, Evaluation, Event
from .store import SQLiteStore
from .runtime import MemoryLearningRuntime

from .providers import ModelProvider, OpenAICompatibleProvider
from .api import serve
