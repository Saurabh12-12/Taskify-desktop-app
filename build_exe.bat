@echo off
echo 🤖 Taskify EXE Builder
echo ================================

REM 
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python not found!
    echo 💡 Install Python from python.org
    pause
    exit /b 1
)

REM 
echo 📦 Checking PyInstaller...
python -m pip install pyinstaller --quiet --upgrade

REM 
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist Taskify_App.spec del Taskify_App.spec

REM 
echo 🔨 Building Taskify.exe...
python -m PyInstaller --onefile --windowed --noconsole ^
    --name "Taskify" ^
    --distpath dist ^
    --clean ^
    Taskify_App.py

if %errorlevel% equ 0 (
    echo ✅ SUCCESS! Taskify.exe created in dist/
    echo 📱 Double-click dist\Taskify.exe to test
) else (
    echo ❌ Build failed!
)

pause
