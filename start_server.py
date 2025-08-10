#!/usr/bin/env python3
"""
Start the Hackathon API server
"""
import os
import uvicorn

# Set up SQLite database for development
os.environ["DATABASE_URL"] = "sqlite:///./hackathon.db"

if __name__ == "__main__":
    print("🚀 Starting Hackathon API server...")
    print("📊 API Documentation will be available at: http://localhost:8000/docs")
    print("📋 ReDoc documentation at: http://localhost:8000/redoc")
    print("🔗 API root at: http://localhost:8000/")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

