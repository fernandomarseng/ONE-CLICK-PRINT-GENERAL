@echo off
setlocal

set "SCRIPT_PATH=%~dp0Run One-Click Print.bat"
set "KEY=HKCU\Software\Classes\Directory\Background\shell\ONE-CLICK-PRINT-GENERAL"

if not exist "%SCRIPT_PATH%" (
    echo Could not find:
    echo   %SCRIPT_PATH%
    echo.
    echo Make sure this installer is in the same folder as "Run One-Click Print.bat".
    pause
    exit /b 1
)

reg add "%KEY%" /ve /d "ONE-CLICK-PRINT-GENERAL" /f >nul
reg add "%KEY%" /v "Icon" /d "imageres.dll,-5324" /f >nul
reg add "%KEY%\command" /ve /d "cmd.exe /c """"%SCRIPT_PATH%"" ""%%V""""" /f >nul

if errorlevel 1 (
    echo Failed to add context menu entry.
    pause
    exit /b 1
)

echo Context menu entry installed:
echo   Show more options ^> ONE-CLICK-PRINT-GENERAL
echo.
echo Right-click empty space inside any folder to use it.
pause

endlocal & exit /b 0
