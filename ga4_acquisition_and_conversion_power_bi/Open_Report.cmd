@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Set-DataFolder.ps1"
if errorlevel 1 pause
