# github.com/safouane02 — session-restore
import sys
import os
import subprocess
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


def detach_from_terminal():
    if os.environ.get("SR_DETACHED") == "1":
        log.debug("already detached, skipping")
        return

    if sys.executable.lower().endswith("pythonw.exe"):
        log.debug("running under pythonw, no detach needed")
        return

    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.isfile(pythonw):
        log.warning("pythonw.exe not found at %s, continuing in current process", pythonw)
        return

    env = os.environ.copy()
    env["SR_DETACHED"] = "1"

    log.debug("relaunching under pythonw: %s", pythonw)
    subprocess.Popen(
        [pythonw] + sys.argv,
        env=env,
        close_fds=True,
        creationflags=subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP,
    )
    sys.exit(0)


def is_already_running():
    try:
        import psutil
        current = psutil.Process()
        for proc in psutil.process_iter(["name", "pid"]):
            if proc.info["name"] == current.name() and proc.pid != current.pid:
                log.debug("duplicate instance found (pid %s), aborting", proc.pid)
                return True
        return False
    except Exception as e:
        log.error("is_already_running failed: %s", e)
        return False


def main():
    log.info("startup — executable: %s", sys.executable)

    detach_from_terminal()

    if is_already_running():
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Session Restore", "Session Restore is already running in the background.")
        root.destroy()
        return

    log.info("initializing components")

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