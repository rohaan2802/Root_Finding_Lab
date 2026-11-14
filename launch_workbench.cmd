@echo off
setlocal
cd /d "%~dp0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m rootlab.desktop
) else (
    python -m rootlab.desktop
)
if errorlevel 1 pause
