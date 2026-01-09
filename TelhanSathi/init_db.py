#!/usr/bin/env python3
"""
Database initialization script - runs before Flask app starts
This creates all tables automatically if they don't exist
"""
import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def init_db():
    """Initialize database - create all tables"""
    try:
        from app import app, db
        
        with app.app_context():
            # Create all tables
            print("[DB INIT] Creating database tables...")
            db.create_all()
            print("[DB INIT] ✓ Database initialized successfully!")
            return True
    except Exception as e:
        print(f"[DB INIT] ✗ Error initializing database: {e}")
        return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)
