# github.com/safouane02 — session-restore
import os
import threading
from pathlib import Path

from models import SessionSnapshot, WindowInfo, FolderInfo
from native import (
    enum_windows,
    is_window_visible,
    get_window_text,
    get_window_rect,
    get_window_process_id,
    get_executable_path,
)

SYSTEM_PROCESSES = {
    "explorer", "dwm", "taskmgr", "svchost", "csrss",
    "winlogon", "lsass", "services", "sessionrestore",
}


class SnapshotEngine:
    def __init__(self, storage, interval_seconds=30):
        self._storage = storage
        self._interval = interval_seconds
        self._timer = None
        self._running = False

    def start(self):
        self._running = True
        self._schedule()

    def stop(self):
        self._running = False
        if self._timer:
            self._timer.cancel()

    def capture(self):
        snap = SessionSnapshot.create()
        snap.windows = self._get_open_windows()
        snap.open_folders = self._get_open_explorer_folders()
        return snap

    def _schedule(self):
        if not self._running:
            return
        self._capture_and_save()
        self._timer = threading.Timer(self._interval, self._schedule)
        self._timer.daemon = True
        self._timer.start()

    def _capture_and_save(self):
        try:
            snap = self.capture()
            self._storage.save_snapshot(snap)
        except Exception:
            pass

    def _get_open_windows(self):
        seen_paths = set()
        windows = []

        for hwnd in enum_windows(None):
            if not is_window_visible(hwnd):
                continue

            title = get_window_text(hwnd)
            if not title:
                continue

            pid = get_window_process_id(hwnd)
            if not pid:
                continue

            exe_path = get_executable_path(pid)
            proc_name = Path(exe_path).stem.lower() if exe_path else ""

            if proc_name in SYSTEM_PROCESSES:
                continue

            if exe_path in seen_paths:
                continue

            rect = get_window_rect(hwnd)
            width = rect.right - rect.left
            height = rect.bottom - rect.top

            if width <= 0 or height <= 0:
                continue

            seen_paths.add(exe_path)
            windows.append(WindowInfo(
                process_name=proc_name,
                executable_path=exe_path,
                window_title=title,
                x=rect.left,
                y=rect.top,
                width=width,
                height=height,
            ))

        return windows

    def _get_open_explorer_folders(self):
        folders = []
        try:
            import win32com.client
            shell = win32com.client.Dispatch("Shell.Application")
            for win in shell.Windows():
                try:
                    location = win.LocationURL
                    if location and location.startswith("file:///"):
                        from urllib.request import url2pathname
                        path = url2pathname(location.replace("file:///", ""))
                        if os.path.isdir(path):
                            folders.append(FolderInfo(path=path))
                except Exception:
                    pass
        except Exception:
            pass
        return folders
