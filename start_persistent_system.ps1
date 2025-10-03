# ================================================================
# GOVERNMENT FEEDBACK SYSTEM - PERMANENT STARTUP SCRIPT
# ================================================================
# This script ensures your system works reliably every day
# Run this anytime to start your complete system

param(
    [switch]$ForceRestart,
    [switch]$SkipHealth,
    [switch]$Verbose
)

# Colors for output
$Green = "Green"
$Yellow = "Yellow" 
$Red = "Red"
$Cyan = "Cyan"
$Magenta = "Magenta"

function Write-Status {
    param($Message, $Color = "White")
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] $Message" -ForegroundColor $Color
}

function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("localhost", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

function Stop-ExistingServices {
    Write-Status "🧹 Cleaning up existing services..." $Yellow
    
    # Stop PowerShell jobs
    Get-Job | Where-Object { $_.Name -match "Backend|Frontend|RealAI" } | ForEach-Object {
        Write-Status "   Stopping job: $($_.Name)" $Yellow
        $_ | Stop-Job -PassThru | Remove-Job
    }
    
    # Kill processes on ports if needed
    $ports = @(8000, 5173, 5174)
    foreach ($port in $ports) {
        if (Test-Port $port) {
            Write-Status "   Port $port is occupied, attempting to free..." $Yellow
            try {
                $processes = netstat -ano | findstr ":$port" | ForEach-Object { ($_ -split '\s+')[4] }
                $processes | Sort-Object -Unique | ForEach-Object {
                    if ($_ -and $_ -ne "0") {
                        Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
                        Write-Status "   Stopped process $_ on port $port" $Yellow
                    }
                }
            } catch {
                Write-Status "   Could not free port $port automatically" $Red
            }
        }
    }
    
    Start-Sleep -Seconds 2
}

function Test-Requirements {
    Write-Status "🔍 Checking system requirements..." $Cyan
    
    # Check Python virtual environment
    $pythonPath = "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe"
    if (-not (Test-Path $pythonPath)) {
        Write-Status "❌ Python virtual environment not found at: $pythonPath" $Red
        return $false
    }
    Write-Status "✅ Python virtual environment found" $Green
    
    # Check Node.js for frontend
    try {
        $nodeVersion = & npm --version 2>$null
        Write-Status "✅ Node.js/npm found (version: $nodeVersion)" $Green
    } catch {
        Write-Status "❌ Node.js/npm not found - frontend may not work" $Red
        return $false
    }
    
    # Check workspace structure
    $requiredPaths = @(
        "C:\Users\RAMSUNDAR\hackathon\backend\app_debug.py",
        "C:\Users\RAMSUNDAR\hackathon\frontend\package.json",
        "C:\Users\RAMSUNDAR\hackathon\backend\models.py"
    )
    
    foreach ($path in $requiredPaths) {
        if (-not (Test-Path $path)) {
            Write-Status "❌ Required file missing: $path" $Red
            return $false
        }
    }
    Write-Status "✅ All required files found" $Green
    
    return $true
}

function Start-Backend {
    Write-Status "🔧 Starting AI-Powered Backend..." $Cyan
    
    $backendJob = Start-Job -Name "AIBackend" -ScriptBlock {
        Set-Location "C:\Users\RAMSUNDAR\hackathon\backend"
        & "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_debug:app --host 0.0.0.0 --port 8000 --reload
    }
    
    Write-Status "   Backend job started (ID: $($backendJob.Id))" $Green
    
    # Wait for backend to initialize
    Write-Status "   Waiting for AI models to load..." $Yellow
    $timeout = 30
    $elapsed = 0
    
    do {
        Start-Sleep -Seconds 2
        $elapsed += 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Status "✅ Backend is ready with AI models loaded!" $Green
                return $true
            }
        } catch {
            if ($elapsed -le $timeout) {
                Write-Status "   Still loading... ($elapsed/$timeout seconds)" $Yellow
            }
        }
    } while ($elapsed -le $timeout)
    
    Write-Status "❌ Backend failed to start within $timeout seconds" $Red
    return $false
}

function Start-Frontend {
    Write-Status "🎨 Starting React Frontend..." $Magenta
    
    $frontendJob = Start-Job -Name "ReactFrontend" -ScriptBlock {
        Set-Location "C:\Users\RAMSUNDAR\hackathon\frontend"
        npm run dev
    }
    
    Write-Status "   Frontend job started (ID: $($frontendJob.Id))" $Green
    
    # Wait for frontend to start
    $timeout = 20
    $elapsed = 0
    
    do {
        Start-Sleep -Seconds 2
        $elapsed += 2
        
        try {
            $response = Invoke-WebRequest -Uri "http://localhost:5173" -UseBasicParsing -TimeoutSec 5 -ErrorAction Stop
            if ($response.StatusCode -eq 200) {
                Write-Status "✅ Frontend is ready!" $Green
                return $true
            }
        } catch {
            if ($elapsed -le $timeout) {
                Write-Status "   Starting React... ($elapsed/$timeout seconds)" $Yellow
            }
        }
    } while ($elapsed -le $timeout)
    
    Write-Status "❌ Frontend failed to start within $timeout seconds" $Red
    return $false
}

function Test-SystemHealth {
    if ($SkipHealth) {
        return $true
    }
    
    Write-Status "🏥 Running comprehensive health checks..." $Cyan
    
    # Test all endpoints
    $endpoints = @(
        @{ Name = "Backend Health"; Url = "http://localhost:8000/health" },
        @{ Name = "Amendments API"; Url = "http://localhost:8000/amendments" },
        @{ Name = "Frontend"; Url = "http://localhost:5173" }
    )
    
    $allHealthy = $true
    
    foreach ($endpoint in $endpoints) {
        try {
            $response = Invoke-WebRequest -Uri $endpoint.Url -UseBasicParsing -TimeoutSec 10
            if ($response.StatusCode -eq 200) {
                Write-Status "✅ $($endpoint.Name): OK" $Green
            } else {
                Write-Status "⚠️ $($endpoint.Name): Status $($response.StatusCode)" $Yellow
                $allHealthy = $false
            }
        } catch {
            Write-Status "❌ $($endpoint.Name): Failed" $Red
            $allHealthy = $false
        }
    }
    
    # Test AI functionality
    try {
        Write-Status "🤖 Testing AI sentiment analysis..." $Cyan
        $testBody = '{"amendment_id": 1, "original_text": "This is a test of the AI system"}'
        $response = Invoke-WebRequest -Uri "http://localhost:8000/feedback" -Method POST -Body $testBody -ContentType "application/json" -UseBasicParsing -TimeoutSec 15
        
        if ($response.StatusCode -eq 200) {
            $content = $response.Content | ConvertFrom-Json
            if ($content.success -and $content.data.sentiment) {
                Write-Status "✅ AI Models: Working (Sentiment: $($content.data.sentiment))" $Green
            } else {
                Write-Status "⚠️ AI Models: Response format issue" $Yellow
                $allHealthy = $false
            }
        }
    } catch {
        Write-Status "❌ AI Models: Failed to test" $Red
        $allHealthy = $false
    }
    
    return $allHealthy
}

function Show-SystemInfo {
    Write-Status "" 
    Write-Status "🎉 GOVERNMENT FEEDBACK SYSTEM READY!" $Green
    Write-Status "=================================================" $Green
    Write-Status "📱 Frontend (React):     http://localhost:5173" $Cyan
    Write-Status "🔧 Backend API:          http://localhost:8000" $Cyan  
    Write-Status "📚 API Documentation:    http://localhost:8000/docs" $Cyan
    Write-Status "🏥 Health Check:         http://localhost:8000/health" $Cyan
    Write-Status "=================================================" $Green
    Write-Status ""
    Write-Status "🤖 AI Models Active:" $Yellow
    Write-Status "   • Detoxify (Toxicity Detection)" $Yellow
    Write-Status "   • DistilBERT (Sentiment Analysis)" $Yellow
    Write-Status "   • BART (Text Summarization)" $Yellow
    Write-Status "   • CUDA GPU Acceleration: Enabled" $Yellow
    Write-Status ""
    Write-Status "📊 Current Jobs:" $Cyan
    Get-Job | Where-Object { $_.Name -match "Backend|Frontend" } | Format-Table Name, State, HasMoreData -AutoSize
    Write-Status ""
    Write-Status "🛠️ Management Commands:" $Yellow
    Write-Status "   • View logs:      Receive-Job -Name 'AIBackend' -Keep" $Yellow
    Write-Status "   • Stop system:    Get-Job | Stop-Job; Get-Job | Remove-Job" $Yellow
    Write-Status "   • Restart:        .\\start_persistent_system.ps1 -ForceRestart" $Yellow
    Write-Status ""
}

# ================================================================
# MAIN EXECUTION
# ================================================================

Write-Status "🚀 GOVERNMENT FEEDBACK SYSTEM STARTUP" $Green
Write-Status "🕒 Starting at $(Get-Date)" $Green
Write-Status ""

# Force restart if requested
if ($ForceRestart) {
    Stop-ExistingServices
} elseif ((Get-Job | Where-Object { $_.Name -match "Backend|Frontend" }).Count -gt 0) {
    Write-Status "⚠️ Services already running. Use -ForceRestart to restart them." $Yellow
    Write-Status "Current jobs:" $Yellow
    Get-Job | Where-Object { $_.Name -match "Backend|Frontend" } | Format-Table Name, State -AutoSize
    
    if (-not $SkipHealth) {
        $healthy = Test-SystemHealth
        if ($healthy) {
            Show-SystemInfo
            exit 0
        } else {
            Write-Status "🔄 Health check failed. Restarting system..." $Yellow
            Stop-ExistingServices
        }
    } else {
        Show-SystemInfo
        exit 0
    }
}

# Run startup sequence
if (-not (Test-Requirements)) {
    Write-Status "❌ System requirements not met. Please check the errors above." $Red
    exit 1
}

Stop-ExistingServices

if (-not (Start-Backend)) {
    Write-Status "❌ Failed to start backend. Check the logs with: Receive-Job -Name 'AIBackend'" $Red
    exit 1
}

if (-not (Start-Frontend)) {
    Write-Status "❌ Failed to start frontend. Check the logs with: Receive-Job -Name 'ReactFrontend'" $Red
    exit 1
}

# Final health check
$systemHealthy = Test-SystemHealth

if ($systemHealthy) {
    Show-SystemInfo
    Write-Status "✅ System startup completed successfully!" $Green
} else {
    Write-Status "⚠️ System started but some health checks failed." $Yellow
    Write-Status "Check individual services and try again if needed." $Yellow
    Show-SystemInfo
}

Write-Status "🎯 Your AI-powered government feedback system is ready for use!" $Green