from app import app
from extensions import db
from sqlalchemy import text

with app.app_context():
    try:
        print('=== Buyer Table Columns ===')
        result = db.session.execute(text('PRAGMA table_info(buyers)')).fetchall()
        for col in result:
            print(f'  {col[1]}: {col[2]}')
        
        print('\n=== Chat Table Columns ===')
        result = db.session.execute(text('PRAGMA table_info(chats)')).fetchall()
        for col in result:
            print(f'  {col[1]}: {col[2]}')
        
        print('\n=== ChatMessage Table Columns ===')
        result = db.session.execute(text('PRAGMA table_info(chat_messages)')).fetchall()
        for col in result:
            print(f'  {col[1]}: {col[2]}')
    except Exception as e:
        print(f'Error: {e}')
