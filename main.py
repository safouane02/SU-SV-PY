# github.com/safouane02 — session-restore
import sys
import os
import subprocess
import tkinter as tk
from tkinter import messagebox

from core import StorageManager, SnapshotEngine, RestoreEngine
from ui import RestorePromptWindow, TrayIcon


def detach_from_terminal():
    if os.environ.get("SR_DETACHED") == "1":
        return

    if sys.executable.lower().endswith("pythonw.exe"):
        return

    pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
    if not os.path.isfile(pythonw):
        return

    env = os.environ.copy()
    env["SR_DETACHED"] = "1"

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
                return True
        return False
    except Exception:
        return False


def main():
    detach_from_terminal()

    if is_already_running():
        root = tk.Tk()
        root.withdraw()
        messagebox.showinfo("Session Restore", "Session Restore is already running in the background.")
        root.destroy()
        return

    storage = StorageManager()
    snapshot_engine = SnapshotEngine(storage, interval_seconds=30)
    restore_engine = RestoreEngine()

    if storage.was_previous_shutdown_unexpected():
        last_session = storage.load_last_snapshot()
        if last_session is not None:
            prompt = RestorePromptWindow(last_session)
            if prompt.show():
                restore_engine.restore_session(last_session)

    storage.clear_shutdown_flag()
    snapshot_engine.start()

    tray = TrayIcon(snapshot_engine, storage)
    tray.run()


if __name__ == "__main__":
    main()