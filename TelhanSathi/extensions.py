from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

# Import eventlet to make it available for SocketIO
try:
    import eventlet
    eventlet.monkey_patch()
except ImportError:
    pass  # eventlet not required if not installed

# Create db instance without app context to avoid circular imports
db = SQLAlchemy()

# Create SocketIO instance without app context to avoid circular imports
# async_mode=None will auto-detect: eventlet > gevent > threading
socketio = SocketIO(
    cors_allowed_origins="*",  # Allow all origins (adjust in production)
    async_mode=None,            # Auto-detect async mode (eventlet preferred)
    ping_timeout=60,
    ping_interval=25,
    logger=False,               # Reduce logging noise
    engineio_logger=False       # Reduce EngineIO logging
)
