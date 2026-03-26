# github.com/safouane02 — session-restore
import os
import subprocess

from models import SessionSnapshot, WindowInfo, FolderInfo


class RestoreEngine:
    def restore_session(self, snapshot: SessionSnapshot):
        for folder in snapshot.open_folders:
            self._restore_folder(folder)

        running = self._get_running_process_names()
        for window in snapshot.windows:
            self._restore_application(window, running)

    def _restore_folder(self, folder: FolderInfo):
        if not os.path.isdir(folder.path):
            return
        subprocess.Popen(["explorer.exe", folder.path])

    def _restore_application(self, window: WindowInfo, running_processes: set):
        if not window.executable_path:
            return
        if not os.path.isfile(window.executable_path):
            return
        if window.process_name in running_processes:
            return

        try:
            subprocess.Popen([window.executable_path], shell=True)
        except Exception:
            pass

    def _get_running_process_names(self):
        try:
            import psutil
            return {p.name().lower().replace(".exe", "") for p in psutil.process_iter(["name"])}
        except Exception:
            return set()
