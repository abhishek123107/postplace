# Simple Gunicorn configuration for development
# Usage: gunicorn -c gunicorn_config.py wsgi

import multiprocessing

# Server socket
bind = "0.0.0.0:8000"

# Worker processes
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000

# Timeout
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"

# Process naming
proc_name = "postify-dev"

# Auto-reload for development
reload = True
reload_engine = "auto"
reload_extra_files = []

# Graceful shutdown
graceful_timeout = 30

# Worker temp directory
worker_tmp_dir = "/dev/shm"
