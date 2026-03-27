#!/usr/bin/env python3
"""
Database initialization script - runs before Flask app starts
This creates all tables automatically if they don't exist
"""
import os
import sys
import time
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def init_db():
    """Initialize database - create all tables with retry logic"""
    max_retries = 5
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            from app import app, db
            
            with app.app_context():
                print("[DB INIT] ========================================")
                print("[DB INIT] Starting database initialization...")
                db_url = os.getenv('DATABASE_URL', 'sqlite:///telhan_sathi.db')
                print(f"[DB INIT] DATABASE_URL: {db_url[:60]}...")
                print(f"[DB INIT] Using SQLAlchemy URI: {app.config['SQLALCHEMY_DATABASE_URI'][:60]}...")
                
                # Create all tables
                print("[DB INIT] Creating database tables...")
                db.create_all()
                
                # Verify tables were created
                inspector = db.inspect(db.engine)
                tables = inspector.get_table_names()
                print(f"[DB INIT] ✓ Created {len(tables)} tables: {', '.join(tables[:5])}{'...' if len(tables) > 5 else ''}")
                print("[DB INIT] ✓ Database initialized successfully!")
                print("[DB INIT] ========================================")
                return True
            
        except Exception as e:
            retry_count += 1
            if retry_count < max_retries:
                wait_time = 3 * retry_count  # Exponential backoff: 3, 6, 9, 12, 15 seconds
                print(f"[DB INIT] ⚠ Attempt {retry_count}/{max_retries} failed: {type(e).__name__}")
                print(f"[DB INIT] Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                print(f"[DB INIT] ✗ ERROR after {max_retries} attempts: {type(e).__name__}: {str(e)}")
                import traceback
                print("[DB INIT] Traceback:")
                traceback.print_exc()
                print("[DB INIT] ========================================")
                return False

if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)

