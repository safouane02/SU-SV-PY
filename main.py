# github.com/safouane02 — session-restore
import sys
import os
import logging
import tkinter as tk
from tkinter import messagebox

from core import StorageManager, SnapshotEngine, RestoreEngine
from ui import RestorePromptWindow, TrayIcon

log_path = os.path.join(os.environ.get("APPDATA", "."), "SessionRestore", "debug.log")
os.makedirs(os.path.dirname(log_path), exist_ok=True)
logging.basicConfig(
    filename=log_path,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s — %(message)s",
)
log = logging.getLogger(__name__)

LOCK_FILE = os.path.join(os.environ.get("APPDATA", "."), "SessionRestore", "session_restore.lock")


def acquire_lock():
    import atexit
    if os.path.exists(LOCK_FILE):
        try:
            with open(LOCK_FILE) as f:
                pid = int(f.read().strip())
            import psutil
            if psutil.pid_exists(pid):
                log.debug("another instance is running (pid %s)", pid)
                return False
        except Exception:
            pass

    with open(LOCK_FILE, "w") as f:
        f.write(str(os.getpid()))

    atexit.register(lambda: os.remove(LOCK_FILE) if os.path.exists(LOCK_FILE) else None)
    return True


def main():
    log.info("startup — executable: %s", sys.executable)

    if not acquire_lock():
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Session Restore", "Session Restore is already running in the background.")
        root.destroy()
        return

    log.info("lock acquired, initializing")

    storage = StorageManager()
    snapshot_engine = SnapshotEngine(storage, interval_seconds=30)
    restore_engine = RestoreEngine()

    if storage.was_previous_shutdown_unexpected():
        log.info("unexpected shutdown detected, loading last session")
        last_session = storage.load_last_snapshot()
        if last_session is not None:
            prompt = RestorePromptWindow(last_session)
            if prompt.show():
                log.info("user chose to restore session")
                restore_engine.restore_session(last_session)

    storage.clear_shutdown_flag()
    snapshot_engine.start()
    log.info("snapshot engine started, launching tray icon")

    tray = TrayIcon(snapshot_engine, storage)
    tray.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        log.exception("fatal error: %s", e)