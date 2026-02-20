#!/bin/bash
# Postify Backend Startup Script with Gunicorn

# Set environment variables
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
export ENVIRONMENT=production

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Warning: Virtual environment is not activated!"
    echo "Please activate your virtual environment first:"
    echo "source .venv/bin/activate  # Linux/Mac"
    echo ".venv\\Scripts\\activate  # Windows"
    exit 1
fi

# Install dependencies if needed
echo "Installing dependencies..."
pip install -r requirements.txt

# Start Gunicorn with configuration
echo "Starting Postify backend with Gunicorn..."
gunicorn -c gunicorn.conf.py app.main:app

# Alternative commands for different environments:

# Development (with auto-reload):
# gunicorn -c gunicorn_config.py app.main:app

# Production (optimized):
# gunicorn -c gunicorn.conf.py app.main:app

# Simple production:
# gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 app.main:app

# Docker production:
# gunicorn -c gunicorn.conf.py app.main:app --bind 0.0.0.0:8000
