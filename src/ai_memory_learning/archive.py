from __future__ import annotations
import hashlib, json
from pathlib import Path
from .models import MessageRecord

class AppendOnlyArchive:
    """Lossless, line-oriented source-of-truth archive for canonical messages."""
    def __init__(self, path):
        self.path = Path(path); self.path.parent.mkdir(parents=True, exist_ok=True)
    def append(self, message):
        if self.contains(message.message_id): raise ValueError(f"message already archived: {message.message_id}")
        record={**message.canonical_payload(), "content_hash":message.content_hash}
        with self.path.open("a",encoding="utf-8") as f: f.write(json.dumps(record,sort_keys=True,ensure_ascii=False)+"\n")
    def contains(self, message_id):
        if not self.path.exists(): return False
        with self.path.open(encoding="utf-8") as f:
            return any(json.loads(x)["message_id"]==message_id for x in f if x.strip())
    def manifest(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest() if self.path.exists() else hashlib.sha256(b"").hexdigest()
    def verify(self):
        bad=[]
        if not self.path.exists(): return bad
        from datetime import datetime
        with self.path.open(encoding="utf-8") as f:
            for line in f:
                if not line.strip(): continue
                r=json.loads(line); m=MessageRecord(r["message_id"],r["conversation_id"],r["sequence_no"],r["role"],r["content"],datetime.fromisoformat(r["timestamp"]),r["schema_version"],r.get("parent_id"))
                if m.content_hash != r["content_hash"]: bad.append(m.message_id)
        return bad
