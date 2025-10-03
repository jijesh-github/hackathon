# PowerShell script to start both servers in separate jobs
param(
    [switch]$CUDA = $false,
    [switch]$Stop = $false
)

$ProjectRoot = "C:\Users\RAMSUNDAR\hackathon"
$BackendDir = "$ProjectRoot\backend"
$FrontendDir = "$ProjectRoot\frontend" 
$VenvPython = "$ProjectRoot\.venv\Scripts\python.exe"

function Stop-AllServers {
    Write-Host "🛑 Stopping all servers..." -ForegroundColor Red
    
    # Stop PowerShell jobs
    Get-Job | Where-Object { $_.Name -like "*Server*" } | Stop-Job
    Get-Job | Where-Object { $_.Name -like "*Server*" } | Remove-Job
    
    # Stop any remaining processes
    Get-Process | Where-Object {
        $_.ProcessName -like "*python*" -or 
        $_.ProcessName -like "*uvicorn*" -or 
        $_.ProcessName -like "*node*"
    } | Stop-Process -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ All servers stopped" -ForegroundColor Green
}

function Start-BackendServer {
    param([string]$AppName = "app_fixed")
    
    Write-Host "📡 Starting backend server..." -ForegroundColor Blue
    
    $BackendJob = Start-Job -Name "BackendServer" -ScriptBlock {
        param($BackendDir, $VenvPython, $AppName)
        Set-Location $BackendDir
        & $VenvPython -m uvicorn "$AppName`:app" --host 127.0.0.1 --port 8000
    } -ArgumentList $BackendDir, $VenvPython, $AppName
    
    Start-Sleep -Seconds 3
    Write-Host "✅ Backend job started (ID: $($BackendJob.Id))" -ForegroundColor Green
    return $BackendJob
}

function Start-FrontendServer {
    Write-Host "🎨 Starting frontend server..." -ForegroundColor Blue
    
    $FrontendJob = Start-Job -Name "FrontendServer" -ScriptBlock {
        param($FrontendDir)
        Set-Location $FrontendDir
        npm run dev
    } -ArgumentList $FrontendDir
    
    Start-Sleep -Seconds 2
    Write-Host "✅ Frontend job started (ID: $($FrontendJob.Id))" -ForegroundColor Green
    return $FrontendJob
}

function Show-ServerStatus {
    Write-Host "`n🎉 Amendment Feedback System Status:" -ForegroundColor Yellow
    Write-Host "=" * 50 -ForegroundColor Yellow
    
    $jobs = Get-Job | Where-Object { $_.Name -like "*Server*" }
    foreach ($job in $jobs) {
        $status = if ($job.State -eq "Running") { "✅ Running" } else { "❌ $($job.State)" }
        Write-Host "$($job.Name): $status" -ForegroundColor $(if ($job.State -eq "Running") { "Green" } else { "Red" })
    }
    
    Write-Host "`n🌐 Access URLs:" -ForegroundColor Cyan
    Write-Host "📱 Frontend: http://localhost:5173" -ForegroundColor White
    Write-Host "🔧 Backend API: http://127.0.0.1:8000" -ForegroundColor White
    Write-Host "📊 Health Check: http://127.0.0.1:8000/health" -ForegroundColor White
    
    if ($CUDA) {
        Write-Host "🚀 CUDA Acceleration: ENABLED" -ForegroundColor Green
    } else {
        Write-Host "⚡ Mode: Lightweight (Fast)" -ForegroundColor Yellow
    }
    
    Write-Host "`n💡 Commands:" -ForegroundColor Cyan
    Write-Host "   Get-Job                    # Check job status" -ForegroundColor Gray
    Write-Host "   .\start_servers.ps1 -Stop # Stop all servers" -ForegroundColor Gray
}

# Main execution
if ($Stop) {
    Stop-AllServers
    exit
}

# Stop any existing servers first
Stop-AllServers
Start-Sleep -Seconds 2

# Start servers
if ($CUDA) {
    Write-Host "🚀 Starting with CUDA acceleration..." -ForegroundColor Magenta
    $backendJob = Start-BackendServer -AppName "app_cuda"
} else {
    Write-Host "⚡ Starting in lightweight mode..." -ForegroundColor Yellow
    $backendJob = Start-BackendServer -AppName "app_fixed" 
}

$frontendJob = Start-FrontendServer

# Show status
Start-Sleep -Seconds 3
Show-ServerStatus

Write-Host "`n✨ System is ready! Press Ctrl+C to stop or run with -Stop flag" -ForegroundColor Green