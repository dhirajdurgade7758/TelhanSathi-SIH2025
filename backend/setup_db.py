from app import app
from extensions import db

with app.app_context():
    db.drop_all()
    db.create_all()
    print('✓ Database created successfully with all tables!')
    print('✓ Chat tables are now available')
