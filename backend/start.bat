@echo off
REM Postify Backend Startup Script for Windows with Gunicorn

REM Set environment variables
set PYTHONPATH=%PYTHONPATH%;%CD%
set ENVIRONMENT=production

REM Check if virtual environment is activated
if "%VIRTUAL_ENV%"=="" (
    echo Warning: Virtual environment is not activated!
    echo Please activate your virtual environment first:
    echo .venv\Scripts\activate
    pause
    exit /b 1
)

REM Install dependencies if needed
echo Installing dependencies...
pip install -r requirements.txt

REM Start Gunicorn with configuration
echo Starting Postify backend with Gunicorn...
gunicorn -c gunicorn.conf.py postify.wsgi

REM Alternative commands for different environments:

REM Development (with auto-reload):
REM gunicorn -c gunicorn_config.py postify.wsgi

REM Production (optimized):
REM gunicorn -c gunicorn.conf.py postify.wsgi

REM Simple production:
REM gunicorn --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000 postify.wsgi

pause
