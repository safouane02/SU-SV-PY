# github.com/safouane02 — session-restore
import json
import os
from pathlib import Path

from models import SessionSnapshot


class StorageManager:
    def __init__(self):
        self.data_dir = Path(os.environ["APPDATA"]) / "SessionRestore"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.snapshot_path = self.data_dir / "last_session.json"
        self.shutdown_flag = self.data_dir / ".clean_shutdown"

    def save_snapshot(self, snapshot: SessionSnapshot):
        with open(self.snapshot_path, "w", encoding="utf-8") as f:
            json.dump(snapshot.to_dict(), f, ensure_ascii=False, indent=2)

    def load_last_snapshot(self):
        if not self.snapshot_path.exists():
            return None
        try:
            with open(self.snapshot_path, "r", encoding="utf-8") as f:
                return SessionSnapshot.from_dict(json.load(f))
        except Exception:
            return None

    def was_previous_shutdown_unexpected(self):
        return not self.shutdown_flag.exists()

    def mark_clean_shutdown(self):
        self.shutdown_flag.write_text("ok")

    def clear_shutdown_flag(self):
        if self.shutdown_flag.exists():
            self.shutdown_flag.unlink()
