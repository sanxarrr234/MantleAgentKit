import logging
from datetime import datetime
from threading import Lock

log = logging.getLogger(__name__)

MAX_HISTORY = 100


class Storage:
    def __init__(self):
        self.lock = Lock()
        self.data = {
            "latest": None,
            "history": [],
            "errors": [],
            "started_at": datetime.utcnow().isoformat() + "Z",
        }

    def save_snapshot(self, snapshot: dict):
        with self.lock:
            self.data["latest"] = snapshot
            self.data["history"].append(snapshot)
            if len(self.data["history"]) > MAX_HISTORY:
                self.data["history"] = self.data["history"][-MAX_HISTORY:]

    def save_error(self, error: str, loop: int):
        with self.lock:
            self.data["errors"].append({
                "loop": loop,
                "error": error,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
            if len(self.data["errors"]) > 50:
                self.data["errors"] = self.data["errors"][-50:]

    def get_latest(self) -> dict:
        with self.lock:
            return self.data.get("latest")

    def get_history(self) -> list:
        with self.lock:
            return self.data.get("history", [])

    def get_status(self) -> dict:
        with self.lock:
            latest = self.data.get("latest")
            return {
                "started_at": self.data.get("started_at"),
                "loop_count": latest.get("loop", 0) if latest else 0,
                "last_poll": latest.get("timestamp") if latest else None,
                "uptime_seconds": latest.get("uptime_seconds", 0) if latest else 0,
                "error_count": len(self.data.get("errors", [])),
                "status": "running",
            }
