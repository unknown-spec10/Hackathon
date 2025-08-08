#!/usr/bin/env python3
"""
Start the Streamlit UI for testing the Hackathon API - Direct Function Calls
"""
import subprocess
import sys
import os

def main():
    print("🚀 Starting Streamlit UI for Hackathon API Tester (Direct Functions)...")
    print("📊 UI will be available at: http://localhost:8501")
    print("🔗 No API server required - using direct function calls!")
    print("\nPress Ctrl+C to stop the UI\n")
    
    # Set up environment
    os.environ["DATABASE_URL"] = "sqlite:///./hackathon.db"
    
    # Start Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "streamlit_ui_direct.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Streamlit UI stopped")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

if __name__ == "__main__":
    main()
