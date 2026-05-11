import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List

from src.database.connection import get_connection, initialize_database


class EventStore:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._initialize()

    def _initialize(self) -> None:
        initialize_database()

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        safe_payload = json.dumps(payload, ensure_ascii=False)
        created_at = datetime.utcnow().isoformat(timespec="seconds")
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO events (event_type, payload, created_at) VALUES (?, ?, ?)",
                (event_type, safe_payload, created_at),
            )
            conn.commit()

    def list_events(self, limit: int = 30) -> List[Dict[str, Any]]:
        with get_connection() as conn:
            rows = conn.execute(
                "SELECT id, event_type, payload, created_at FROM events ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        result: List[Dict[str, Any]] = []
        for row in rows:
            try:
                payload_obj = json.loads(row["payload"])
            except json.JSONDecodeError:
                payload_obj = {"raw": row["payload"]}
            result.append(
                {
                    "id": row["id"],
                    "event_type": row["event_type"],
                    "payload": payload_obj,
                    "created_at": row["created_at"],
                }
            )
        return result
