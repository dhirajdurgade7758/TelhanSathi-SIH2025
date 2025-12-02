import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'telhan_sathi.db')

print('Using DB at:', DB_PATH)
if not os.path.exists(DB_PATH):
    print('ERROR: Database file not found at', DB_PATH)
    raise SystemExit(1)

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

# Check existing columns
cur.execute("PRAGMA table_info('farmers')")
cols = [r[1] for r in cur.fetchall()]
print('Existing columns:', cols)

if 'onboarding_completed' in cols:
    print('Column onboarding_completed already exists; nothing to do.')
else:
    try:
        cur.execute("ALTER TABLE farmers ADD COLUMN onboarding_completed BOOLEAN DEFAULT 0;")
        conn.commit()
        print('Successfully added onboarding_completed column.')
    except Exception as e:
        print('Failed to add column:', e)

conn.close()
