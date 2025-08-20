#!/usr/bin/env python3
"""
CodeBench Performance Analyzer - Startup Script

This script starts the Streamlit web application for CodeBench.
"""

import subprocess
import sys
import os

def main():
    """Start the Streamlit application"""
    try:
        # Change to the script directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Try to find the correct Python executable
        python_exe = None
        
        # First try virtual environment
        venv_python = os.path.join(script_dir, '.venv', 'bin', 'python')
        if os.path.exists(venv_python):
            python_exe = venv_python
        else:
            # Fall back to system Python
            python_exe = sys.executable
        
        # Start Streamlit
        print("🚀 Starting CodeBench Performance Analyzer...")
        print("📱 The web interface will open in your browser automatically.")
        print("🔗 If it doesn't open, navigate to: http://localhost:8501")
        print("⏹️  Press Ctrl+C to stop the application")
        print("-" * 50)
        
        subprocess.run([
            python_exe, "-m", "streamlit", "run", "app.py",
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
        
    except KeyboardInterrupt:
        print("\n👋 CodeBench stopped. Thanks for using it!")
    except Exception as e:
        print(f"❌ Error starting CodeBench: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
