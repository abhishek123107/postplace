# Postify WSGI entry point for Gunicorn
# This file allows Gunicorn to properly import the FastAPI app

import sys
import os

# Add backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

# Import the FastAPI app from app.main
from app.main import app

# Gunicorn expects a WSGI application, but we're using FastAPI
# This wrapper makes it compatible
application = app

# For direct execution (development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
