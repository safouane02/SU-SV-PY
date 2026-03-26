# github.com/safouane02 — session-restore
import tkinter as tk
from datetime import datetime

from models import SessionSnapshot


class RestorePromptWindow:
    def __init__(self, snapshot: SessionSnapshot):
        self.snapshot = snapshot
        self.user_wants_restore = False
        self._build()

    def _build(self):
        self.root = tk.Tk()
        self.root.title("Session Restore")
        self.root.geometry("440x225")
        self.root.resizable(False, False)
        self.root.configure(bg="white")
        self.root.attributes("-topmost", True)
        self.root.eval("tk::PlaceWindow . center")

        captured = datetime.fromisoformat(self.snapshot.captured_at)
        delta = datetime.now() - captured
        minutes = int(delta.total_seconds() / 60)
        ago = "less than a minute ago" if minutes < 2 else f"{minutes} minutes ago"

        tk.Label(
            self.root,
            text="Restore previous session?",
            font=("Segoe UI", 13, "bold"),
            bg="white",
            fg="#141414",
            anchor="w",
        ).place(x=20, y=20)

        details = (
            f"Last saved: {ago}\n"
            f"{len(self.snapshot.windows)} apps  \u2022  {len(self.snapshot.open_folders)} folders"
        )
        tk.Label(
            self.root,
            text=details,
            font=("Segoe UI", 9),
            bg="white",
            fg="#646464",
            justify="left",
            anchor="w",
        ).place(x=20, y=60)

        tk.Frame(self.root, bg="#dcdcdc", height=1).place(x=0, y=145, relwidth=1)

        restore_btn = tk.Button(
            self.root,
            text="Restore Session",
            font=("Segoe UI", 9),
            bg="#0078d4",
            fg="white",
            relief="flat",
            activebackground="#106ebe",
            activeforeground="white",
            cursor="hand2",
            command=self._on_restore,
        )
        restore_btn.place(x=20, y=167, width=140, height=36)

        skip_btn = tk.Button(
            self.root,
            text="Skip",
            font=("Segoe UI", 9),
            bg="white",
            fg="#3c3c3c",
            relief="solid",
            bd=1,
            cursor="hand2",
            command=self._on_skip,
        )
        skip_btn.place(x=172, y=167, width=70, height=36)

        self.root.protocol("WM_DELETE_WINDOW", self._on_skip)

    def show(self):
        self.root.mainloop()
        return self.user_wants_restore

    def _on_restore(self):
        self.user_wants_restore = True
        self.root.destroy()

    def _on_skip(self):
        self.user_wants_restore = False
        self.root.destroy()
