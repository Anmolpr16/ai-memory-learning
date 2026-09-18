from datetime import datetime, timezone
from ai_memory_learning.archive import AppendOnlyArchive
from ai_memory_learning.models import MessageRecord
def test_archive_roundtrip_and_integrity(tmp_path):
    a=AppendOnlyArchive(tmp_path/'messages.jsonl');m=MessageRecord('m1','c1',1,'user','hello memory',datetime.now(timezone.utc));a.append(m);assert a.contains('m1');assert a.verify()==[];assert len(a.manifest())==64
