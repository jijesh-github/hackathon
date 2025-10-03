#!/usr/bin/env python3
"""
Simple server starter script to avoid terminal issues
"""
import sys
import os
import subprocess

def start_server():
    try:
        # Get the virtual environment path
        venv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.venv')
        python_exe = os.path.join(venv_path, 'Scripts', 'python.exe')
        
        # Start the server
        cmd = [python_exe, '-m', 'uvicorn', 'app_fixed:app', '--host', '127.0.0.1', '--port', '8000']
        
        print("🚀 Starting backend server...")
        print(f"Command: {' '.join(cmd)}")
        
        # Run the server
        process = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return process.returncode
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit_code = start_server()
    sys.exit(exit_code)