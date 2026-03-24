from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Create db instance without app context to avoid circular imports
db = SQLAlchemy()

# Create SocketIO instance without app context to avoid circular imports
socketio = SocketIO(
    cors_allowed_origins="*",  # Allow all origins (adjust in production)
    async_mode='threading',     # Use threading for simplicity
    ping_timeout=60,
    ping_interval=25
)
