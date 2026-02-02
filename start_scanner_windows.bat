@echo off
REM Windows Startup Script for Epstein Files GitHub Scanner
REM Place this in your Windows Startup folder or schedule via Task Scheduler

echo ========================================
echo EPSTEIN FILES - GITHUB SCANNER
echo Starting automated monitoring...
echo ========================================
echo.

REM Change to the directory where your scripts are located
cd /d "%~dp0"

REM Run the scheduler (keeps running in background)
python auto_scheduler.py

REM If the script exits, wait before closing
pause
