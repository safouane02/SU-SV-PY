# session-restore

A lightweight Windows background utility that saves your open windows and folders every 30 seconds,
then offers to bring them back after an unexpected shutdown or power loss — the same way Chrome
restores your tabs.

## How it works

Every 30 seconds the app snapshots:
- All visible application windows (name, exe path, position, size)
- All open File Explorer folders via Shell COM

On a normal shutdown it writes a clean-exit flag. On next boot, if that flag is missing
(power cut, crash, freeze), a prompt appears asking if you want your session back.

## Quick start

```bash
pip install -r requirements.txt
python main.py
```

## Build a standalone exe

```bash
build.bat
```

Output: `dist/SessionRestore.exe` — no Python needed on the target machine.

## Auto-start with Windows

Drop a shortcut to the exe in:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup
```

## Project layout

```
session-restore/
├── main.py
├── requirements.txt
├── build.bat
├── core/
│   ├── snapshot_engine.py    captures windows + folders on a timer
│   ├── restore_engine.py     re-launches apps and opens folders
│   └── storage_manager.py   JSON persistence + shutdown flag
├── models/
│   └── session_snapshot.py  dataclasses
├── native/
│   └── win32_api.py         ctypes wrappers for user32 / kernel32
└── ui/
    ├── restore_prompt.py    "Restore session?" dialog
    └── tray_icon.py         system tray icon + menu
```

## Data location

```
%APPDATA%\SessionRestore\last_session.json
```

## Dependencies

| Package | Purpose |
|---|---|
| pywin32 | Shell COM — reading open Explorer folders |
| pystray | system tray icon |
| Pillow | drawing the tray icon image |
| psutil | checking which processes are already running |

## Author

Built by [safouane02](https://github.com/safouane02)
