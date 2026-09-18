from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from .models import MessageRecord
from .retrieval import Retriever
from .store import SQLiteStore
from datetime import datetime, timezone


class MemoryAPIHandler(BaseHTTPRequestHandler):
    server_version = "ai-memory-learning/1.0"

    def _json(self, status: int, payload: object) -> None:
        data = json.dumps(payload, default=str).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:
        if self.path == "/health":
            self._json(200, {"status": "ok", "integrity": self.server.store.integrity_check()})
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0"))
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
            if self.path == "/messages":
                m = MessageRecord(
                    body["message_id"], body["conversation_id"], int(body["sequence_no"]),
                    body.get("role", "user"), body["content"],
                    datetime.fromisoformat(body["timestamp"]) if body.get("timestamp") else datetime.now(timezone.utc),
                    parent_id=body.get("parent_id"),
                )
                self.server.store.add_message(m)
                self._json(201, {"message_id": m.message_id, "content_hash": m.content_hash})
                return
            if self.path == "/search":
                hits = Retriever(self.server.store).search(body["query"], int(body.get("limit", 10)))
                self._json(200, [h.__dict__ for h in hits])
                return
        except (KeyError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self._json(400, {"error": str(exc)})
            return
        self._json(404, {"error": "not found"})

    def log_message(self, *_args):
        return


def serve(db: str = "memory.db", host: str = "127.0.0.1", port: int = 8787) -> None:
    with SQLiteStore(db) as store:
        server = ThreadingHTTPServer((host, port), MemoryAPIHandler)
        server.store = store
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.server_close()
