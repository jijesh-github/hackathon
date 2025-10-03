# ================================================================
# INSTALL GOVERNMENT FEEDBACK SYSTEM AS WINDOWS SERVICE
# ================================================================
# Run this ONCE to install the system as a Windows service
# After this, your system will start automatically on boot

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status
)

function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

function Install-ServiceWrapper {
    Write-Host "🔧 Installing Government Feedback System as Windows Service..." -ForegroundColor Green
    
    # Create service wrapper script
    $serviceScript = @"
# Government Feedback System Service Wrapper
Set-Location "C:\Users\RAMSUNDAR\hackathon"

# Start backend
Start-Job -Name "ServiceBackend" -ScriptBlock {
    Set-Location "C:\Users\RAMSUNDAR\hackathon\backend"
    & "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_debug:app --host 0.0.0.0 --port 8000
}

# Wait for backend
Start-Sleep -Seconds 10

# Start frontend  
Start-Job -Name "ServiceFrontend" -ScriptBlock {
    Set-Location "C:\Users\RAMSUNDAR\hackathon\frontend"
    npm run dev
}

# Keep service running
while (`$true) {
    Start-Sleep -Seconds 30
    
    # Check if jobs are still running
    `$backendJob = Get-Job -Name "ServiceBackend" -ErrorAction SilentlyContinue
    `$frontendJob = Get-Job -Name "ServiceFrontend" -ErrorAction SilentlyContinue
    
    if (-not `$backendJob -or `$backendJob.State -ne "Running") {
        Write-Host "Backend job failed, restarting..."
        Start-Job -Name "ServiceBackend" -ScriptBlock {
            Set-Location "C:\Users\RAMSUNDAR\hackathon\backend"
            & "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -m uvicorn app_debug:app --host 0.0.0.0 --port 8000
        }
    }
    
    if (-not `$frontendJob -or `$frontendJob.State -ne "Running") {
        Write-Host "Frontend job failed, restarting..."
        Start-Job -Name "ServiceFrontend" -ScriptBlock {
            Set-Location "C:\Users\RAMSUNDAR\hackathon\frontend"
            npm run dev
        }
    }
}
"@

    $serviceScript | Out-File -FilePath "C:\Users\RAMSUNDAR\hackathon\service_wrapper.ps1" -Encoding UTF8
    
    # Create service using NSSM (Non-Sucking Service Manager)
    Write-Host "📦 Creating Windows Service..." -ForegroundColor Cyan
    
    $serviceName = "GovernmentFeedbackSystem"
    $serviceDisplayName = "Government Feedback System"
    $serviceDescription = "AI-powered government amendment feedback system with React frontend and FastAPI backend"
    
    # Check if NSSM is available
    try {
        $nssmPath = Get-Command nssm -ErrorAction Stop
        Write-Host "✅ NSSM found at: $($nssmPath.Source)" -ForegroundColor Green
    } catch {
        Write-Host "❌ NSSM not found. Installing NSSM..." -ForegroundColor Yellow
        Write-Host "Please install NSSM manually from: https://nssm.cc/download" -ForegroundColor Yellow
        Write-Host "Or use chocolatey: choco install nssm" -ForegroundColor Yellow
        return $false
    }
    
    # Remove existing service if it exists
    $existingService = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    if ($existingService) {
        Write-Host "🗑️ Removing existing service..." -ForegroundColor Yellow
        & nssm remove $serviceName confirm
    }
    
    # Install new service
    & nssm install $serviceName powershell
    & nssm set $serviceName Application powershell.exe
    & nssm set $serviceName AppParameters "-ExecutionPolicy Bypass -File `"C:\Users\RAMSUNDAR\hackathon\service_wrapper.ps1`""
    & nssm set $serviceName AppDirectory "C:\Users\RAMSUNDAR\hackathon"
    & nssm set $serviceName DisplayName $serviceDisplayName
    & nssm set $serviceName Description $serviceDescription
    & nssm set $serviceName Start SERVICE_AUTO_START
    & nssm set $serviceName AppStdout "C:\Users\RAMSUNDAR\hackathon\service.log"
    & nssm set $serviceName AppStderr "C:\Users\RAMSUNDAR\hackathon\service_error.log"
    
    Write-Host "✅ Service installed successfully!" -ForegroundColor Green
    Write-Host "🚀 Starting service..." -ForegroundColor Cyan
    
    Start-Service -Name $serviceName
    
    Write-Host "✅ Government Feedback System is now running as a Windows Service!" -ForegroundColor Green
    Write-Host "   • Service Name: $serviceName" -ForegroundColor Cyan
    Write-Host "   • Auto-start: Enabled" -ForegroundColor Cyan
    Write-Host "   • Logs: C:\Users\RAMSUNDAR\hackathon\service.log" -ForegroundColor Cyan
    
    return $true
}

function Uninstall-ServiceWrapper {
    Write-Host "🗑️ Uninstalling Government Feedback System service..." -ForegroundColor Yellow
    
    $serviceName = "GovernmentFeedbackSystem"
    
    try {
        Stop-Service -Name $serviceName -Force -ErrorAction SilentlyContinue
        & nssm remove $serviceName confirm
        Write-Host "✅ Service uninstalled successfully!" -ForegroundColor Green
    } catch {
        Write-Host "❌ Failed to uninstall service: $($_.Exception.Message)" -ForegroundColor Red
    }
}

function Show-ServiceStatus {
    $serviceName = "GovernmentFeedbackSystem"
    
    $service = Get-Service -Name $serviceName -ErrorAction SilentlyContinue
    
    if ($service) {
        Write-Host "📊 Service Status:" -ForegroundColor Cyan
        Write-Host "   Name: $($service.Name)" -ForegroundColor White
        Write-Host "   Status: $($service.Status)" -ForegroundColor $(if ($service.Status -eq "Running") { "Green" } else { "Red" })
        Write-Host "   Start Type: $($service.StartType)" -ForegroundColor White
        
        if (Test-Path "C:\Users\RAMSUNDAR\hackathon\service.log") {
            Write-Host "📝 Recent logs:" -ForegroundColor Yellow
            Get-Content "C:\Users\RAMSUNDAR\hackathon\service.log" -Tail 10
        }
    } else {
        Write-Host "❌ Service not installed" -ForegroundColor Red
    }
}

# ================================================================
# MAIN EXECUTION  
# ================================================================

if (-not (Test-Administrator)) {
    Write-Host "❌ This script requires administrator privileges." -ForegroundColor Red
    Write-Host "Please run PowerShell as Administrator and try again." -ForegroundColor Yellow
    exit 1
}

if ($Install) {
    Install-ServiceWrapper
} elseif ($Uninstall) {
    Uninstall-ServiceWrapper
} elseif ($Status) {
    Show-ServiceStatus
} else {
    Write-Host "Government Feedback System - Service Manager" -ForegroundColor Green
    Write-Host "Usage:" -ForegroundColor White
    Write-Host "  -Install    Install as Windows Service (auto-start on boot)" -ForegroundColor Cyan
    Write-Host "  -Uninstall  Remove the Windows Service" -ForegroundColor Cyan
    Write-Host "  -Status     Show service status and logs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Example: .\install_service.ps1 -Install" -ForegroundColor Yellow
}