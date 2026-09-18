from datetime import datetime,timezone
from ai_memory_learning import *
def test_sqlite_message_search(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        s.add_message(MessageRecord('m','c',1,'user','durable memory archive',datetime.now(timezone.utc)))
        assert s.get_message('m').content=='durable memory archive'
        assert s.search_messages('memory')[0].message_id=='m'
def test_event_hash_and_integrity(tmp_path):
    with SQLiteStore(tmp_path/'m.db') as s:
        e=Event('x','test',datetime.now(timezone.utc),{'a':1});s.add_event(e);assert s.integrity_check()=='ok'
