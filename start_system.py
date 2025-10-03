#!/usr/bin/env python3
"""
Stable server runner that bypasses VS Code terminal issues
"""
import subprocess
import sys
import os
import time
import signal
from pathlib import Path

def start_servers():
    """Start both frontend and backend servers in stable way"""
    
    # Get paths
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"  
    frontend_dir = project_root / "frontend"
    venv_python = project_root / ".venv" / "Scripts" / "python.exe"
    
    print("🚀 Starting Amendment Feedback System...")
    print("=" * 50)
    
    processes = []
    
    try:
        # Start backend server
        print("📡 Starting backend server...")
        backend_cmd = [
            str(venv_python), 
            "-m", "uvicorn", 
            "app_cuda:app", 
            "--host", "127.0.0.1", 
            "--port", "8000"
        ]
        
        backend_process = subprocess.Popen(
            backend_cmd,
            cwd=str(backend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        processes.append(("Backend", backend_process))
        print(f"✅ Backend started (PID: {backend_process.pid})")
        
        # Wait a moment for backend to start
        time.sleep(3)
        
        # Start frontend server  
        print("🎨 Starting frontend server...")
        frontend_cmd = ["npm", "run", "dev"]
        
        frontend_process = subprocess.Popen(
            frontend_cmd,
            cwd=str(frontend_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        processes.append(("Frontend", frontend_process))
        print(f"✅ Frontend started (PID: {frontend_process.pid})")
        
        print("\n🎉 System is running!")
        print("📱 Frontend: http://localhost:5173")
        print("🔧 Backend: http://127.0.0.1:8000")
        print("🚀 CUDA Models: Loaded on GPU")
        print("\nPress Ctrl+C to stop all servers")
        
        # Wait for user interrupt
        while True:
            time.sleep(1)
            
            # Check if processes are still alive
            for name, process in processes:
                if process.poll() is not None:
                    print(f"⚠️ {name} process ended unexpectedly")
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down servers...")
        
        for name, process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                print(f"✅ {name} stopped")
            except:
                try:
                    process.kill()
                    print(f"🔫 {name} force stopped")
                except:
                    pass
                    
        print("✅ All servers stopped")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    sys.exit(start_servers())