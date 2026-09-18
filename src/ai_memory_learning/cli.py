from __future__ import annotations
import argparse, json
from datetime import datetime, timezone
from .models import MessageRecord, Lesson
from .store import SQLiteStore
from .retrieval import Retriever
from .export import export_jsonl, export_manifest
from .preservation import PreservationManager
from .api import serve

def main():
    ap=argparse.ArgumentParser(prog='aimemory',description='Durable AI memory and experiential-learning reference runtime')
    sub=ap.add_subparsers(dest='cmd',required=True)
    p=sub.add_parser('init'); p.add_argument('db')
    p=sub.add_parser('message'); p.add_argument('db'); p.add_argument('message_id'); p.add_argument('conversation_id'); p.add_argument('content'); p.add_argument('--role',choices=['system','user','assistant','tool'],default='user'); p.add_argument('--sequence',type=int,default=1); p.add_argument('--parent-id')
    p=sub.add_parser('search'); p.add_argument('db'); p.add_argument('query'); p.add_argument('-n','--limit',type=int,default=10)
    p=sub.add_parser('lesson'); p.add_argument('db'); p.add_argument('lesson_id'); p.add_argument('condition'); p.add_argument('action'); p.add_argument('expected_effect'); p.add_argument('observed_effect'); p.add_argument('--confidence',type=float,default=0.0)
    p=sub.add_parser('verify'); p.add_argument('db')
    p=sub.add_parser('export'); p.add_argument('db'); p.add_argument('path')
    p=sub.add_parser('manifest'); p.add_argument('db'); p.add_argument('path')
    p=sub.add_parser('snapshot'); p.add_argument('db'); p.add_argument('path')
    p=sub.add_parser('restore-test'); p.add_argument('snapshot')
    p=sub.add_parser('serve'); p.add_argument('db'); p.add_argument('--host',default='127.0.0.1'); p.add_argument('--port',type=int,default=8787)
    a=ap.parse_args()
    if a.cmd=='init':
        with SQLiteStore(a.db): pass
        print(f'initialized {a.db}')
    elif a.cmd=='message':
        with SQLiteStore(a.db) as s:
            m=MessageRecord(a.message_id,a.conversation_id,a.sequence,a.role,a.content,datetime.now(timezone.utc),parent_id=a.parent_id); s.add_message(m); print(m.content_hash)
    elif a.cmd=='search':
        with SQLiteStore(a.db) as s:
            for h in Retriever(s).search(a.query,a.limit): print(f'{h.kind}\t{h.record_id}\t{h.score:.2f}\t{h.reason}')
    elif a.cmd=='lesson':
        if not 0<=a.confidence<=1: raise SystemExit('confidence must be between 0 and 1')
        with SQLiteStore(a.db) as s: s.add_lesson(Lesson(a.lesson_id,a.condition,a.action,a.expected_effect,a.observed_effect,0,a.confidence)); print(a.lesson_id)
    elif a.cmd=='verify':
        with SQLiteStore(a.db) as s: print(s.integrity_check())
    elif a.cmd=='export':
        with SQLiteStore(a.db) as s: print(export_jsonl(s,a.path))
    elif a.cmd=='manifest':
        with SQLiteStore(a.db) as s: print(export_manifest(s,a.path))
    elif a.cmd=='snapshot':
        with SQLiteStore(a.db) as s: print(json.dumps(PreservationManager(s).snapshot(a.path),indent=2))
    elif a.cmd=='restore-test': print('ok' if PreservationManager.sha256(a.snapshot) and __import__('sqlite3').connect(a.snapshot).execute('PRAGMA integrity_check').fetchone()[0]=='ok' else 'failed')
    elif a.cmd=='serve': serve(a.db,a.host,a.port)
if __name__=='__main__': main()
