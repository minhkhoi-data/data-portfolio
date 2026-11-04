@echo off
cd /d "%~dp0"
where py >nul 2>nul
if not errorlevel 1 (
  py -3 scripts\setup_env.py
) else (
  python scripts\setup_env.py
)
if errorlevel 1 echo Setup failed. Read BAT_DAU.md and the message above.
pause
