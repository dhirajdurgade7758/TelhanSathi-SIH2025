# Helper to create all DB tables in development when migrations are not available
# Run from repository root (backend folder):
# & ".venv\Scripts\python.exe" "scripts\create_db_tables.py"

import os
import sys

# Ensure project root (parent of this scripts/ folder) is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from extensions import db

if __name__ == '__main__':
    with app.app_context():
        print('Creating all tables using SQLAlchemy metadata (db.create_all())...')
        db.create_all()
        print('Done. Tables created (if they did not exist).')
