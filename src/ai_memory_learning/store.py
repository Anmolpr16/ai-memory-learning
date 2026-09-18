from __future__ import annotations
import json, sqlite3
from pathlib import Path
from dataclasses import asdict
from .models import *

SCHEMA='''
PRAGMA journal_mode=WAL;
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS messages(message_id TEXT PRIMARY KEY, conversation_id TEXT NOT NULL, sequence_no INTEGER NOT NULL, role TEXT NOT NULL, content TEXT NOT NULL, timestamp TEXT NOT NULL, schema_version INTEGER NOT NULL, parent_id TEXT, content_hash TEXT NOT NULL);
CREATE VIRTUAL TABLE IF NOT EXISTS messages_fts USING fts5(message_id UNINDEXED, content, conversation_id UNINDEXED, role UNINDEXED);
CREATE TABLE IF NOT EXISTS experiences(experience_id TEXT PRIMARY KEY, timestamp TEXT NOT NULL, context_hash TEXT NOT NULL, goal TEXT NOT NULL, action TEXT NOT NULL, prediction TEXT NOT NULL, outcome TEXT NOT NULL, reward REAL, failure_type TEXT, verification_status TEXT NOT NULL, confidence REAL NOT NULL, lesson_id TEXT);
CREATE TABLE IF NOT EXISTS evidence(experience_id TEXT NOT NULL, source_id TEXT NOT NULL, message_ids TEXT NOT NULL, notes TEXT, PRIMARY KEY(experience_id,source_id), FOREIGN KEY(experience_id) REFERENCES experiences(experience_id));
CREATE TABLE IF NOT EXISTS lessons(lesson_id TEXT PRIMARY KEY, condition TEXT NOT NULL, action TEXT NOT NULL, expected_effect TEXT NOT NULL, observed_effect TEXT NOT NULL, evidence_count INTEGER NOT NULL, confidence REAL NOT NULL, exceptions TEXT NOT NULL, last_verified TEXT, source_experience_ids TEXT NOT NULL, contradiction_ids TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS evaluations(evaluation_id TEXT PRIMARY KEY, experience_id TEXT NOT NULL, status TEXT NOT NULL, score REAL NOT NULL, evaluator TEXT NOT NULL, rationale TEXT NOT NULL, evidence TEXT NOT NULL, FOREIGN KEY(experience_id) REFERENCES experiences(experience_id));
CREATE TABLE IF NOT EXISTS skills(skill_id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT NOT NULL, procedure TEXT NOT NULL, preconditions TEXT NOT NULL, regression_tests TEXT NOT NULL, confidence REAL NOT NULL, verified INTEGER NOT NULL);
CREATE TABLE IF NOT EXISTS facts(fact_id TEXT PRIMARY KEY, subject TEXT NOT NULL, predicate TEXT NOT NULL, value TEXT NOT NULL, source_ids TEXT NOT NULL, confidence REAL NOT NULL, valid_from TEXT, valid_to TEXT);
CREATE TABLE IF NOT EXISTS relationships(relationship_id TEXT PRIMARY KEY, subject_id TEXT NOT NULL, predicate TEXT NOT NULL, object_id TEXT NOT NULL, source_ids TEXT NOT NULL, confidence REAL NOT NULL);
CREATE TABLE IF NOT EXISTS events(event_id TEXT PRIMARY KEY, event_type TEXT NOT NULL, timestamp TEXT NOT NULL, payload TEXT NOT NULL, schema_version INTEGER NOT NULL, event_hash TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS metadata(key TEXT PRIMARY KEY,value TEXT NOT NULL);
CREATE INDEX IF NOT EXISTS idx_messages_conversation_seq ON messages(conversation_id,sequence_no);
CREATE INDEX IF NOT EXISTS idx_experiences_status ON experiences(verification_status);
CREATE INDEX IF NOT EXISTS idx_lessons_confidence ON lessons(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_facts_subject_predicate ON facts(subject,predicate);
CREATE INDEX IF NOT EXISTS idx_relationships_subject ON relationships(subject_id);
CREATE INDEX IF NOT EXISTS idx_relationships_object ON relationships(object_id);
'''

class SQLiteStore:
    def __init__(self,path='memory.db'):
        self.path=Path(path); self.path.parent.mkdir(parents=True,exist_ok=True)
        self.conn=sqlite3.connect(self.path, check_same_thread=False); self.conn.row_factory=sqlite3.Row
        self.conn.execute('PRAGMA foreign_keys=ON'); self.conn.executescript(SCHEMA)
    def close(self): self.conn.close()
    def __enter__(self): return self
    def __exit__(self,*_): self.close()
    def add_message(self,m):
        with self.conn:
            self.conn.execute('INSERT INTO messages VALUES(?,?,?,?,?,?,?,?,?)',(m.message_id,m.conversation_id,m.sequence_no,m.role,m.content,m.timestamp.isoformat(),m.schema_version,m.parent_id,m.content_hash))
            self.conn.execute('INSERT INTO messages_fts VALUES(?,?,?,?)',(m.message_id,m.content,m.conversation_id,m.role))
    def get_message(self,i):
        r=self.conn.execute('SELECT * FROM messages WHERE message_id=?',(i,)).fetchone(); return self._message(r) if r else None
    def _message(self,r): return MessageRecord(r['message_id'],r['conversation_id'],r['sequence_no'],r['role'],r['content'],datetime.fromisoformat(r['timestamp']),r['schema_version'],r['parent_id'])
    def search_messages(self,q,limit=20):
        terms=' '.join('"'+x.replace('"','')+'"' for x in q.split() if x)
        if not terms:return []
        rows=self.conn.execute('SELECT m.* FROM messages_fts f JOIN messages m ON m.message_id=f.message_id WHERE messages_fts MATCH ? ORDER BY bm25(messages_fts),m.sequence_no LIMIT ?',(terms,limit)).fetchall()
        return [self._message(r) for r in rows]
    def add_experience(self,e):
        with self.conn:
            self.conn.execute('INSERT INTO experiences VALUES(?,?,?,?,?,?,?,?,?,?,?,?)',(e.experience_id,e.timestamp.isoformat(),e.context_hash,e.goal,e.action,e.prediction,e.outcome,e.reward,e.failure_type,e.verification_status,e.confidence,e.lesson_id))
            for x in e.evidence:self.conn.execute('INSERT INTO evidence VALUES(?,?,?,?)',(e.experience_id,x.source_id,json.dumps(x.message_ids),x.notes))
    def update_experience(self,e):
        with self.conn:self.conn.execute('UPDATE experiences SET timestamp=?,context_hash=?,goal=?,action=?,prediction=?,outcome=?,reward=?,failure_type=?,verification_status=?,confidence=?,lesson_id=? WHERE experience_id=?',(e.timestamp.isoformat(),e.context_hash,e.goal,e.action,e.prediction,e.outcome,e.reward,e.failure_type,e.verification_status,e.confidence,e.lesson_id,e.experience_id))
    def get_experience(self,i):
        r=self.conn.execute('SELECT * FROM experiences WHERE experience_id=?',(i,)).fetchone()
        if not r:return None
        ev=tuple(EvidenceRef(x['source_id'],tuple(json.loads(x['message_ids'])),x['notes']) for x in self.conn.execute('SELECT * FROM evidence WHERE experience_id=?',(i,)))
        return Experience(r['experience_id'],datetime.fromisoformat(r['timestamp']),r['context_hash'],r['goal'],r['action'],r['prediction'],r['outcome'],r['reward'],r['failure_type'],ev,r['verification_status'],r['confidence'],r['lesson_id'])
    def iter_experiences(self): return [self.get_experience(r['experience_id']) for r in self.conn.execute('SELECT experience_id FROM experiences ORDER BY timestamp')]
    def add_lesson(self,l):
        with self.conn:self.conn.execute('INSERT INTO lessons VALUES(?,?,?,?,?,?,?,?,?,?,?)',(l.lesson_id,l.condition,l.action,l.expected_effect,l.observed_effect,l.evidence_count,l.confidence,json.dumps(l.exceptions),l.last_verified.isoformat() if l.last_verified else None,json.dumps(l.source_experience_ids),json.dumps(l.contradiction_ids)))
    def update_lesson(self,l):
        with self.conn:self.conn.execute('UPDATE lessons SET condition=?,action=?,expected_effect=?,observed_effect=?,evidence_count=?,confidence=?,exceptions=?,last_verified=?,source_experience_ids=?,contradiction_ids=? WHERE lesson_id=?',(l.condition,l.action,l.expected_effect,l.observed_effect,l.evidence_count,l.confidence,json.dumps(l.exceptions),l.last_verified.isoformat() if l.last_verified else None,json.dumps(l.source_experience_ids),json.dumps(l.contradiction_ids),l.lesson_id))
    def get_lesson(self,i):
        r=self.conn.execute('SELECT * FROM lessons WHERE lesson_id=?',(i,)).fetchone()
        if not r:return None
        return Lesson(r['lesson_id'],r['condition'],r['action'],r['expected_effect'],r['observed_effect'],r['evidence_count'],r['confidence'],tuple(json.loads(r['exceptions'])),datetime.fromisoformat(r['last_verified']) if r['last_verified'] else None,tuple(json.loads(r['source_experience_ids'])),tuple(json.loads(r['contradiction_ids'])))
    def iter_lessons(self): return [self.get_lesson(r['lesson_id']) for r in self.conn.execute('SELECT lesson_id FROM lessons ORDER BY confidence DESC,lesson_id')]
    def add_evaluation(self,e):
        with self.conn:self.conn.execute('INSERT INTO evaluations VALUES(?,?,?,?,?,?,?)',(e.evaluation_id,e.experience_id,e.status,e.score,e.evaluator,e.rationale,json.dumps([asdict(x) for x in e.evidence])))
    def add_skill(self,s):
        with self.conn:self.conn.execute('INSERT INTO skills VALUES(?,?,?,?,?,?,?,?)',(s.skill_id,s.name,s.description,json.dumps(s.procedure),json.dumps(s.preconditions),json.dumps(s.regression_tests),s.confidence,int(s.verified)))
    def add_fact(self,f):
        with self.conn:self.conn.execute('INSERT INTO facts VALUES(?,?,?,?,?,?,?,?)',(f.fact_id,f.subject,f.predicate,f.value,json.dumps(f.source_ids),f.confidence,f.valid_from,f.valid_to))
    def get_fact(self,i):
        from .memory import MemoryFact
        r=self.conn.execute('SELECT * FROM facts WHERE fact_id=?',(i,)).fetchone()
        return MemoryFact(r['fact_id'],r['subject'],r['predicate'],r['value'],tuple(json.loads(r['source_ids'])),r['confidence'],r['valid_from'],r['valid_to']) if r else None
    def iter_facts(self): return [self.get_fact(r['fact_id']) for r in self.conn.execute('SELECT fact_id FROM facts ORDER BY subject,predicate')]
    def search_facts(self,subject=None,predicate=None):
        q='SELECT fact_id FROM facts WHERE 1=1'; args=[]
        if subject is not None:q+=' AND subject=?';args.append(subject)
        if predicate is not None:q+=' AND predicate=?';args.append(predicate)
        return [self.get_fact(r['fact_id']) for r in self.conn.execute(q,args)]
    def add_relationship(self,r):
        with self.conn:self.conn.execute('INSERT INTO relationships VALUES(?,?,?,?,?,?)',(r.relationship_id,r.subject_id,r.predicate,r.object_id,json.dumps(r.source_ids),r.confidence))
    def neighbors(self,entity_id):
        rows=self.conn.execute('SELECT * FROM relationships WHERE subject_id=? OR object_id=?',(entity_id,entity_id)).fetchall()
        from .graph import Relationship
        return [Relationship(r['relationship_id'],r['subject_id'],r['predicate'],r['object_id'],tuple(json.loads(r['source_ids'])),r['confidence']) for r in rows]
    def add_event(self,e):
        with self.conn:self.conn.execute('INSERT INTO events VALUES(?,?,?,?,?,?)',(e.event_id,e.event_type,e.timestamp.isoformat(),json.dumps(e.payload,sort_keys=True),e.schema_version,e.event_hash))
    def iter_events(self): return [dict(r) for r in self.conn.execute('SELECT * FROM events ORDER BY timestamp,event_id')]
    def iter_messages(self): return [self._message(r) for r in self.conn.execute('SELECT * FROM messages ORDER BY conversation_id,sequence_no')]
    def delete_message(self,message_id):
        """Delete from the hot store; callers must coordinate archive/cache/backup deletion policy separately."""
        with self.conn:
            self.conn.execute('DELETE FROM messages_fts WHERE message_id=?',(message_id,)); self.conn.execute('DELETE FROM messages WHERE message_id=?',(message_id,))
    def integrity_check(self): return self.conn.execute('PRAGMA integrity_check').fetchone()[0]
