@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv-vision\Scripts\python.exe" (
 echo Primero ejecutar install_env_windows.cmd
 pause
 exit /b 1
)
.venv-vision\Scripts\python.exe -m vision.server %*
if errorlevel 1 pause
