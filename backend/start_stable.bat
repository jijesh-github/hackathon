@echo off
echo ========================================
echo    Starting Stable Backend Server
echo ========================================
cd /d "C:\Users\RAMSUNDAR\hackathon\backend"
start "Backend Server" cmd /k "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_fixed:app --host 127.0.0.1 --port 8000
echo Backend server started in separate window
timeout /t 3 /nobreak >nul
echo.
echo Backend should be running on http://127.0.0.1:8000
echo Frontend is on http://localhost:5174
echo.
pause