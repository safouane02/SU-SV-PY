@echo off
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

echo.
echo Building...
pyinstaller --onefile --windowed --name SessionRestore main.py

echo.
echo Done. Executable is at dist\SessionRestore.exe
pause
