# github.com/safouane02 — session-restore
import subprocess
import threading
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

import pystray
from PIL import Image, ImageDraw

from core import StorageManager, SnapshotEngine


def _create_icon_image():
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 60, 60], fill="#0078d4")
    draw.rectangle([20, 28, 44, 38], fill="white")
    draw.polygon([(20, 24), (20, 42), (44, 33)], fill="white")
    return img


class TrayIcon:
    def __init__(self, snapshot_engine: SnapshotEngine, storage: StorageManager):
        self._engine = snapshot_engine
        self._storage = storage

        menu = pystray.Menu(
            pystray.MenuItem("Session Restore", None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Save Session Now", self._save_now),
            pystray.MenuItem("View Status", self._show_status),
            pystray.MenuItem("Open Data Folder", self._open_data_dir),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self._exit),
        )

        self._icon = pystray.Icon(
            name="SessionRestore",
            icon=_create_icon_image(),
            title="Session Restore — running in background",
            menu=menu,
        )

    def run(self):
        self._icon.run()

    def _save_now(self):
        snap = self._engine.capture()
        self._storage.save_snapshot(snap)
        self._icon.notify(
            f"Saved {len(snap.windows)} apps and {len(snap.open_folders)} folders.",
            "Session Restore"
        )

    def _show_status(self):
        snap = self._storage.load_last_snapshot()

        def _show():
            root = tk.Tk()
            root.withdraw()
            if snap is None:
                messagebox.showinfo("Session Restore", "No session saved yet.")
            else:
                captured = datetime.fromisoformat(snap.captured_at)
                delta = datetime.now() - captured
                minutes = int(delta.total_seconds() / 60)
                ago = "less than a minute ago" if minutes < 2 else f"{minutes} min ago"
                messagebox.showinfo(
                    "Session Restore",
                    f"Last session: {ago}\n"
                    f"Apps: {len(snap.windows)}\n"
                    f"Folders: {len(snap.open_folders)}"
                )
            root.destroy()

        threading.Thread(target=_show, daemon=True).start()

    def _open_data_dir(self):
        subprocess.Popen(["explorer.exe", str(self._storage.data_dir)])

    def _exit(self):
        self._storage.mark_clean_shutdown()
        self._engine.stop()
        self._icon.stop()
