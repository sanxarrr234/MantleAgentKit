import json
import os
import logging
from datetime import datetime
from threading import Lock

log = logging.getLogger(__name__)

DATA_FILE = "agent_data.json"
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
        self._load()

    def _load(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r") as f:
                    saved = json.load(f)
                    self.data.update(saved)
                log.info(f"Loaded existing data from {DATA_FILE}")
            except Exception as e:
                log.warning(f"Could not load saved data: {e}")

    def _persist(self):
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(self.data, f, indent=2)
        except Exception as e:
            log.error(f"Could not persist data: {e}")

    def save_snapshot(self, snapshot: dict):
        with self.lock:
            self.data["latest"] = snapshot
            self.data["history"].append(snapshot)
            if len(self.data["history"]) > MAX_HISTORY:
                self.data["history"] = self.data["history"][-MAX_HISTORY:]
            self._persist()

    def save_error(self, error: str, loop: int):
        with self.lock:
            self.data["errors"].append({
                "loop": loop,
                "error": error,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            })
            if len(self.data["errors"]) > 50:
                self.data["errors"] = self.data["errors"][-50:]
            self._persist()

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
