# 🚀 Government Feedback System - Daily Usage Guide

## ⚡ Quick Start (Every Day)

### Option 1: Double-Click Startup
```
📁 Go to: C:\Users\RAMSUNDAR\hackathon\
🖱️ Double-click: START_SYSTEM.bat
⏳ Wait 30 seconds for AI models to load
🌐 Browser opens automatically to: http://localhost:5173
```

### Option 2: PowerShell Command
```powershell
cd C:\Users\RAMSUNDAR\hackathon
.\start_persistent_system.ps1
```

## 🔧 System Components

| Component | URL | Purpose |
|-----------|-----|---------|
| **Frontend** | http://localhost:5173 | React UI for public use |
| **Backend API** | http://localhost:8000 | FastAPI with AI models |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Health Check** | http://localhost:8000/health | System status |

## 🤖 AI Features Working

✅ **Real Toxicity Detection** - Detoxify model with CUDA
✅ **Real Sentiment Analysis** - DistilBERT (positive/negative)  
✅ **Real Text Summarization** - BART model
✅ **GPU Acceleration** - Using RTX 4050 efficiently

## 🛠️ Common Issues & Solutions

### ❌ "System not starting tomorrow"
**Cause**: PowerShell jobs lost after restart
**Solution**: Use the startup scripts provided
```powershell
# Quick fix
.\start_persistent_system.ps1 -ForceRestart
```

### ❌ "Port already in use"
**Cause**: Previous processes still running
**Solution**: Scripts automatically handle this
```powershell
# Manual cleanup if needed
Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*"} | Stop-Process -Force
```

### ❌ "AI models not loading"
**Cause**: CUDA/Python environment issues
**Solution**: Check GPU and virtual environment
```powershell
# Test CUDA
cd C:\Users\RAMSUNDAR\hackathon\backend
& "C:\Users\RAMSUNDAR\hackathon\.venv\Scripts\python.exe" -c "import torch; print('CUDA Available:', torch.cuda.is_available())"
```

### ❌ "Database connection failed"
**Cause**: Neon PostgreSQL credentials expired
**Solution**: Database credentials are embedded, should work long-term

## 📊 Monitoring Commands

```powershell
# Check running services
Get-Job | Format-Table Name, State, HasMoreData

# View backend logs
Receive-Job -Name "AIBackend" -Keep

# View frontend logs  
Receive-Job -Name "ReactFrontend" -Keep

# Stop all services
Get-Job | Stop-Job; Get-Job | Remove-Job

# System health test
Invoke-WebRequest -Uri "http://localhost:8000/health"
```

## 🔄 Restart Commands

```powershell
# Gentle restart (if system is running but having issues)
.\start_persistent_system.ps1 -ForceRestart

# Full cleanup restart
Get-Job | Stop-Job; Get-Job | Remove-Job
.\start_persistent_system.ps1

# Skip health checks (faster startup)
.\start_persistent_system.ps1 -SkipHealth
```

## 🏆 Long-term Persistence Options

### Option A: Daily Manual Start (Recommended)
- Use `START_SYSTEM.bat` every morning
- Most reliable for development environment
- Easy to troubleshoot

### Option B: Windows Service (Advanced)
```powershell
# Install as Windows Service (auto-start on boot)
# Run as Administrator:
.\install_service.ps1 -Install

# Check service status
.\install_service.ps1 -Status

# Uninstall service
.\install_service.ps1 -Uninstall
```

## 🎯 Expected Performance

- **Startup Time**: 30-45 seconds (AI model loading)
- **Memory Usage**: ~2GB RAM + 1.3GB GPU
- **Uptime**: Stable for hours/days with job monitoring
- **AI Response**: 1-3 seconds per feedback analysis

## 📱 User Access Points

**For Public Users:**
- Main Interface: http://localhost:5173
- Submit Feedback: http://localhost:5173/feedback
- View Amendments: http://localhost:5173/amendments

**For Administrators:**
- Create Amendments: http://localhost:5173/admin
- API Dashboard: http://localhost:8000/docs

## 🚨 Emergency Recovery

If everything breaks:
```powershell
# Nuclear option - clean restart
cd C:\Users\RAMSUNDAR\hackathon
Get-Process | Where-Object {$_.ProcessName -like "*node*" -or $_.ProcessName -like "*python*"} | Stop-Process -Force
Get-Job | Stop-Job; Get-Job | Remove-Job
Start-Sleep -Seconds 5
.\start_persistent_system.ps1 -ForceRestart
```

## ✅ Daily Checklist

1. **Morning**: Run `START_SYSTEM.bat`
2. **Verify**: Open http://localhost:5173 
3. **Test**: Submit a test feedback to confirm AI working
4. **Monitor**: Check system stays stable throughout day
5. **Evening**: Leave running or stop with `Get-Job | Stop-Job`

Your system is designed to work reliably every day! 🎉