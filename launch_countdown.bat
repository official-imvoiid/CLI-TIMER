@echo off
REM -----------------------------------------
REM Windows Launcher: launch_countdown.bat
REM -----------------------------------------

REM Change directory to script folder
cd /d "%~dp0"

REM Path to python (not pythonw - we want console window)
set PYTHON=python

REM Verify python exists in PATH
where %PYTHON% >nul 2>&1
if errorlevel 1 (
    echo ERROR: python not found in PATH. Please install Python.
    pause
    exit /b 1
)

REM Launch TimeLeft.py and wait for it to complete
"%PYTHON%" "%~dp0TimeLeft.py"

REM Script will exit and close cmd window when Python finishes
exit