#!/usr/bin/env python
"""Clear all cached weather recommendations"""
import sqlite3
import os

db_path = 'instance/telhan_sathi.db'

if not os.path.exists(db_path):
    print('✗ Database file not found')
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables first
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print('Available tables:')
    for t in tables:
        print(f'  - {t[0]}')
    
    # Try to delete from weather_recommendations
    try:
        cursor.execute('DELETE FROM weather_recommendations')
        deleted = cursor.rowcount
        conn.commit()
        print(f'\n✓ Cleared {deleted} cached weather recommendations from database')
    except sqlite3.OperationalError as e:
        print(f'\n✗ Error deleting from weather_recommendation: {e}')
    
    conn.close()
except Exception as e:
    print(f'✗ Error: {e}')
