@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
  echo Run SETUP_ENV.cmd once first, or use an Anaconda Prompt as described in BAT_DAU.md.
  pause
  exit /b 1
)
".venv\Scripts\python.exe" scripts\safe_run.py
if errorlevel 1 (
  echo Build failed or timed out. Read the message above and audit\run.json.
) else (
  echo SQL build and independent validation passed. CSV results are in results\.
)
pause
