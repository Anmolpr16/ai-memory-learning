from datetime import datetime,timezone
from ai_memory_learning import SQLiteStore,MessageRecord
from ai_memory_learning.preservation import PreservationManager

def test_snapshot_can_be_verified(tmp_path):
    db=tmp_path/'m.db'; out=tmp_path/'copy.db'
    with SQLiteStore(db) as s:
        s.add_message(MessageRecord('m','c',1,'user','archive',datetime.now(timezone.utc)))
        r=PreservationManager(s).snapshot(out)
        assert r['integrity']=='ok' and PreservationManager(s).verify_snapshot(out,r['sha256'])
