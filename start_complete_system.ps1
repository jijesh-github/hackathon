# Complete System Startup Script
# This script starts both backend and frontend services

Write-Host "🚀 Starting Government Feedback System..." -ForegroundColor Green

# Stop any existing jobs
Write-Host "🧹 Cleaning up existing processes..." -ForegroundColor Yellow
Get-Job | Where-Object { $_.Name -match "Backend|Frontend" } | Stop-Job -PassThru | Remove-Job

# Start Backend
Write-Host "🔧 Starting Backend API..." -ForegroundColor Cyan
$backendJob = Start-Job -Name "Backend" -ScriptBlock {
    Set-Location "C:\Users\RAMSUNDAR\hackathon\backend"
    & "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_debug:app --host 0.0.0.0 --port 8000
}

# Wait for backend to start
Start-Sleep -Seconds 5

# Start Frontend
Write-Host "🎨 Starting Frontend..." -ForegroundColor Magenta
$frontendJob = Start-Job -Name "Frontend" -ScriptBlock {
    Set-Location "C:\Users\RAMSUNDAR\hackathon\frontend"
    npm run dev
}

# Wait for services to initialize
Write-Host "⏳ Waiting for services to initialize..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

# Check status
Write-Host "📊 Service Status:" -ForegroundColor Green
Get-Job | Where-Object { $_.Name -match "Backend|Frontend" } | Format-Table Name, State

# Test endpoints
Write-Host "🔍 Testing endpoints..." -ForegroundColor Cyan

try {
    $backendHealth = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Backend Health: $($backendHealth.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend Health: Failed" -ForegroundColor Red
}

try {
    $frontendHealth = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5
    Write-Host "✅ Frontend Health: $($frontendHealth.StatusCode)" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend Health: Failed" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎉 System Ready!" -ForegroundColor Green
Write-Host "📱 Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "🔧 Backend API: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API Docs: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "To stop services later, run: Get-Job | Stop-Job; Get-Job | Remove-Job" -ForegroundColor Yellow