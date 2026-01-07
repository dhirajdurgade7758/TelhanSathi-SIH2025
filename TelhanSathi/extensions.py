from flask_sqlalchemy import SQLAlchemy

# Create db instance without app context to avoid circular imports
db = SQLAlchemy()
