"""
WSGI entry point for production deployment
"""
import os
from app import app, start_scheduler

# Start the background scheduler for production
start_scheduler()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
