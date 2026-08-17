@echo off
rem =====================================================
rem  StarDust Echoes - Launcher
rem  Double-click to play. Requires Python 3.11+.
rem =====================================================
cd /d "%~dp0"

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python not found on PATH.
    echo Please install Python 3.11 or newer and check "Add to PATH".
    pause
    exit /b 1
)

echo Launching StarDust Echoes ...
echo (First launch generates assets, please wait)
python run.py

if errorlevel 1 (
    echo.
    echo [ERROR] The game exited with an error.
    echo Scroll up to see the details.
    pause
) else (
    echo.
    echo Thanks for playing. See you among the stars.
    timeout /t 3 >nul
)
