#!/usr/bin/env python3
"""
Clear the Hackathon API database
"""
import os
import sqlite3

def clear_database():
    """Clear the SQLite database file"""
    db_file = "hackathon.db"
    
    if os.path.exists(db_file):
        try:
            os.remove(db_file)
            print(f"✅ Database cleared: {db_file}")
        except Exception as e:
            print(f"❌ Error clearing database: {e}")
    else:
        print(f"ℹ️ Database file not found: {db_file}")

if __name__ == "__main__":
    clear_database()
