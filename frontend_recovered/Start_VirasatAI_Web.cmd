@echo off
title VirasatAI - Taj Mahal Preview
cd /d "%~dp0"

if not exist "C:\dev\flutter\bin\flutter.bat" (
    echo Flutter was not found at C:\dev\flutter.
    echo Check that the Flutter folder has not been moved.
    pause
    exit /b 1
)

echo Starting VirasatAI in Chrome. Please wait...
call "C:\dev\flutter\bin\flutter.bat" run -d chrome --no-pub

echo.
echo VirasatAI preview has stopped. You can close this window.
pause
