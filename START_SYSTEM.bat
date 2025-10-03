@echo off
echo.
echo ===============================================
echo  GOVERNMENT FEEDBACK SYSTEM - QUICK START
echo ===============================================
echo.

cd /d "C:\Users\RAMSUNDAR\hackathon"

echo Starting system...
powershell -ExecutionPolicy Bypass -File "start_persistent_system.ps1"

echo.
echo System startup completed!
echo Press any key to open the frontend...
pause >nul

start http://localhost:5173

echo.
echo Frontend opened in your browser.
echo Keep this window open to monitor the system.
echo.
pause