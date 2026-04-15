@echo off
setlocal

set "KEY=HKCU\Software\Classes\Directory\Background\shell\ONE-CLICK-PRINT-GENERAL"

reg delete "%KEY%" /f >nul 2>&1

if errorlevel 1 (
    echo Context menu entry was not found, or removal failed.
    pause
    exit /b 1
)

echo Context menu entry removed:
echo   Show more options ^> ONE-CLICK-PRINT-GENERAL
pause

endlocal & exit /b 0
