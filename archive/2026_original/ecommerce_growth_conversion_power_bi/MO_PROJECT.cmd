@echo off
setlocal
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0scripts\Open-GA4.ps1"
set "ga4_open_result=%ERRORLEVEL%"
if not "%ga4_open_result%"=="0" (
    echo.
    echo Read the message above. The launcher has not confirmed that Power BI loaded.
    pause
)
exit /b %ga4_open_result%
