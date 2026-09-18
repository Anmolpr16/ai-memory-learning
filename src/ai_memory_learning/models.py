from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib,json
from typing import Any, Literal
Role=Literal['system','user','assistant','tool']; Verification=Literal['unverified','verified','rejected']
def utc_now(): return datetime.now(timezone.utc)
def canonical_json(value): return json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()
def digest(value): return hashlib.sha256(canonical_json(value)).hexdigest()
@dataclass(frozen=True)
class MessageRecord:
    message_id:str; conversation_id:str; sequence_no:int; role:Role; content:str; timestamp:datetime; schema_version:int=1; parent_id:str|None=None; content_hash:str=field(init=False)
    def __post_init__(self): object.__setattr__(self,'content_hash',digest(self.canonical_payload()))
    def canonical_payload(self): return {'message_id':self.message_id,'conversation_id':self.conversation_id,'sequence_no':self.sequence_no,'role':self.role,'content':self.content,'timestamp':self.timestamp.isoformat(),'schema_version':self.schema_version,'parent_id':self.parent_id}
@dataclass(frozen=True)
class EvidenceRef:
    source_id:str; message_ids:tuple[str,...]=(); notes:str|None=None
@dataclass(frozen=True)
class Experience:
    experience_id:str; timestamp:datetime; context_hash:str; goal:str; action:str; prediction:str; outcome:str; reward:float|None; failure_type:str|None; evidence:tuple[EvidenceRef,...]; verification_status:Verification='unverified'; confidence:float=0.0; lesson_id:str|None=None
@dataclass(frozen=True)
class Lesson:
    lesson_id:str; condition:str; action:str; expected_effect:str; observed_effect:str; evidence_count:int; confidence:float; exceptions:tuple[str,...]=(); last_verified:datetime|None=None; source_experience_ids:tuple[str,...]=(); contradiction_ids:tuple[str,...]=()
@dataclass(frozen=True)
class Skill:
    skill_id:str; name:str; description:str; procedure:tuple[str,...]; preconditions:tuple[str,...]=(); regression_tests:tuple[str,...]=(); confidence:float=0.0; verified:bool=False
@dataclass(frozen=True)
class Evaluation:
    evaluation_id:str; experience_id:str; status:Literal['pass','fail','inconclusive']; score:float; evaluator:str; rationale:str; evidence:tuple[EvidenceRef,...]=()
@dataclass(frozen=True)
class Event:
    event_id:str; event_type:str; timestamp:datetime; payload:dict[str,Any]; schema_version:int=1; event_hash:str=field(init=False)
    def __post_init__(self): object.__setattr__(self,'event_hash',digest({'event_id':self.event_id,'event_type':self.event_type,'timestamp':self.timestamp.isoformat(),'payload':self.payload,'schema_version':self.schema_version}))
@dataclass
class MemoryStore:
    messages:dict[str,MessageRecord]=field(default_factory=dict); experiences:dict[str,Experience]=field(default_factory=dict); lessons:dict[str,Lesson]=field(default_factory=dict)
    def add_message(self,m):
        if m.message_id in self.messages: raise ValueError(f'message already exists: {m.message_id}')
        self.messages[m.message_id]=m
    def add_experience(self,e):
        if e.experience_id in self.experiences: raise ValueError(f'experience already exists: {e.experience_id}')
        self.experiences[e.experience_id]=e
    def add_lesson(self,l):
        if l.lesson_id in self.lessons: raise ValueError(f'lesson already exists: {l.lesson_id}')
        self.lessons[l.lesson_id]=l
    def iter_lessons(self): return list(self.lessons.values())
    def iter_experiences(self): return list(self.experiences.values())
    def search_messages(self,q,limit=20):
        terms={x.lower() for x in q.split() if x}
        ranked=[]
        for m in self.messages.values():
            overlap=len(terms & {x.lower() for x in m.content.split()})
            if overlap: ranked.append((overlap,m))
        return [m for _,m in sorted(ranked,key=lambda x:(-x[0],x[1].message_id))[:limit]]
