@echo off
title VirasatAI - Phone Browser Preview
cd /d "%~dp0"

if not exist "build\web\index.html" (
    echo The web preview is not built yet.
    echo Ask Codex to rebuild the web preview before using this launcher.
    pause
    exit /b 1
)

if not exist "C:\Users\MANU AGARWAL\AppData\Local\Programs\Python\Python314\python.exe" (
    echo Python was not found at its current location on this PC.
    pause
    exit /b 1
)

echo Keep this window open while viewing VirasatAI on your phone.
echo Connect your phone and PC to the same Wi-Fi network.
echo On your phone, open http://YOUR-PC-IP:8765 in Chrome.
echo Your current PC IPv4 address is shown below:
ipconfig | findstr /C:"IPv4 Address"
echo.
echo Windows Firewall may ask permission the first time. Allow access on Private networks.
echo Press Ctrl+C here to stop the preview.
echo.
"C:\Users\MANU AGARWAL\AppData\Local\Programs\Python\Python314\python.exe" -m http.server 8765 --bind 0.0.0.0 --directory "build\web"

echo.
echo Phone preview has stopped.
pause
