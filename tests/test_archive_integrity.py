from datetime import datetime, timezone
from ai_memory_learning.archive import AppendOnlyArchive
from ai_memory_learning.models import MessageRecord

def test_archive_detects_tampering(tmp_path):
    p=tmp_path/'archive.jsonl'; a=AppendOnlyArchive(p)
    a.append(MessageRecord('m1','c',1,'user','original',datetime.now(timezone.utc)))
    assert a.verify()==[]
    text=p.read_text().replace('original','tampered'); p.write_text(text)
    assert a.verify()==['m1']
