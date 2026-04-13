```batch
@echo off
echo Building Taskify EXE...
pip install pyinstaller
pyinstaller --onefile --windowed --icon=icon.ico --name "Taskify" Taskify_app.py
echo Done! Check dist/Taskify.exe
pause