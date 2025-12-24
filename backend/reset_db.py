#!/usr/bin/env python
"""Reset database and create fresh"""

from app import app
from extensions import db
import os

def reset_database():
    db_path = 'instance/telhan_sathi.db'
    
    # Remove old database
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print("✅ Old database deleted")
        except Exception as e:
            print(f"⚠️  Could not delete: {e}")
            return False
    
    # Create all tables from models
    with app.app_context():
        try:
            db.create_all()
            print("✅ Fresh database created with all tables")
            
            # List tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"✅ Tables created: {len(tables)}")
            for table in sorted(tables):
                print(f"   - {table}")
            return True
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

if __name__ == '__main__':
    reset_database()
