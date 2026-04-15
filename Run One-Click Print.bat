@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHONUTF8=1"

python "%SCRIPT_DIR%one_click_print_general.py" %*
set "EXITCODE=%ERRORLEVEL%"

if not "%EXITCODE%"=="0" (
    echo.
    echo One-Click Print failed with exit code %EXITCODE%.
    pause
)

endlocal & exit /b %EXITCODE%
