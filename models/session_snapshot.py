# github.com/safouane02 — session-restore
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class WindowInfo:
    process_name: str
    executable_path: str
    window_title: str
    x: int
    y: int
    width: int
    height: int


@dataclass
class FolderInfo:
    path: str


@dataclass
class SessionSnapshot:
    captured_at: str
    windows: list[WindowInfo] = field(default_factory=list)
    open_folders: list[FolderInfo] = field(default_factory=list)
    was_unexpected_shutdown: bool = False

    @staticmethod
    def create():
        return SessionSnapshot(captured_at=datetime.now().isoformat())

    def to_dict(self):
        return {
            "captured_at": self.captured_at,
            "was_unexpected_shutdown": self.was_unexpected_shutdown,
            "windows": [w.__dict__ for w in self.windows],
            "open_folders": [f.__dict__ for f in self.open_folders],
        }

    @staticmethod
    def from_dict(data: dict):
        snap = SessionSnapshot(
            captured_at=data.get("captured_at", ""),
            was_unexpected_shutdown=data.get("was_unexpected_shutdown", False),
        )
        snap.windows = [WindowInfo(**w) for w in data.get("windows", [])]
        snap.open_folders = [FolderInfo(**f) for f in data.get("open_folders", [])]
        return snap
