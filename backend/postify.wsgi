# Postify WSGI entry point for Gunicorn
# This file allows Gunicorn to properly import the FastAPI app

import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the FastAPI app
from app.main import app

# Gunicorn expects a WSGI application, but we're using FastAPI
# This wrapper makes it compatible
application = app

if __name__ == "__main__":
    # For direct execution
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
