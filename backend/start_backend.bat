@echo off
cd /d "C:\Users\RAMSUNDAR\hackathon\backend"
echo Starting Backend Server...
"C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_fixed:app --host 127.0.0.1 --port 8000
pause