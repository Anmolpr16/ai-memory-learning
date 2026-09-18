from __future__ import annotations
import hashlib, shutil, sqlite3
from pathlib import Path

class PreservationManager:
    """Local preservation controls: checkpoint, copy, hash, verify, restore-test."""
    def __init__(self,store): self.store=store
    @staticmethod
    def sha256(path):
        h=hashlib.sha256();
        with open(path,"rb") as f:
            for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
        return h.hexdigest()
    def snapshot(self,target):
        target=Path(target); target.parent.mkdir(parents=True,exist_ok=True)
        self.store.conn.execute("PRAGMA wal_checkpoint(FULL)"); shutil.copy2(self.store.path,target)
        return {"path":str(target),"sha256":self.sha256(target),"integrity":self.store.integrity_check()}
    def verify_snapshot(self,path,expected_sha256): return self.sha256(path)==expected_sha256
    def restore_test(self,snapshot_path):
        con=sqlite3.connect(snapshot_path); result=con.execute("PRAGMA integrity_check").fetchone()[0]; con.close(); return result=="ok"
