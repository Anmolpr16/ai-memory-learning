from __future__ import annotations
import json
from pathlib import Path

def export_jsonl(store,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    with p.open("w",encoding="utf-8") as f:
        for m in store.iter_messages(): f.write(json.dumps({"type":"message","record":m.canonical_payload(),"content_hash":m.content_hash},ensure_ascii=False,sort_keys=True)+"\n")
        for fact in store.iter_facts(): f.write(json.dumps({"type":"fact","record":fact.__dict__},ensure_ascii=False,sort_keys=True)+"\n")
    return p

def export_manifest(store,path):
    p=Path(path); p.parent.mkdir(parents=True,exist_ok=True)
    payload={"format":"ai-memory-learning.export.v1","message_count":len(store.iter_messages()),"fact_count":len(store.iter_facts()),"integrity":store.integrity_check()}
    p.write_text(json.dumps(payload,indent=2)+"\n",encoding="utf-8"); return p
