@echo off
echo =========================================
echo    CUDA-Accelerated AI Backend Server
echo =========================================
echo GPU: NVIDIA GeForce RTX 4050 Laptop GPU
echo CUDA: Version 11.8
echo =========================================
echo.
cd /d "C:\Users\RAMSUNDAR\hackathon\backend"
echo Starting CUDA-accelerated server...
echo.
"C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_cuda:app --host 127.0.0.1 --port 8000
echo.
echo Server stopped. Press any key to exit...
pause