import json
import threading
import urllib.request
from http.server import ThreadingHTTPServer
from ai_memory_learning.api import MemoryAPIHandler
from ai_memory_learning.store import SQLiteStore


def test_api_health_and_message(tmp_path):
    db = tmp_path / "memory.db"
    store = SQLiteStore(db)
    server = ThreadingHTTPServer(("127.0.0.1", 0), MemoryAPIHandler)
    server.store = store
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        with urllib.request.urlopen(base + "/health") as r:
            assert json.load(r)["status"] == "ok"
        payload = json.dumps({"message_id":"m1","conversation_id":"c1","sequence_no":1,"content":"hello memory"}).encode()
        req = urllib.request.Request(base + "/messages", data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req) as r:
            assert r.status == 201
        payload = json.dumps({"query":"hello"}).encode()
        req = urllib.request.Request(base + "/search", data=payload, headers={"Content-Type":"application/json"}, method="POST")
        with urllib.request.urlopen(req) as r:
            assert json.load(r)[0]["record_id"] == "m1"
    finally:
        server.shutdown(); server.server_close(); store.close()
