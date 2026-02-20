# Gunicorn configuration file for Postify backend
# Usage: gunicorn -c gunicorn.conf.py postify.wsgi

import multiprocessing
import os

# Server socket
bind = "0.0.0.0:8000"
backlog = 2048

# Worker processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "postify-backend"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (if needed)
# keyfile = "/path/to/keyfile"
# certfile = "/path/to/certfile"

# Graceful shutdown
graceful_timeout = 30
timeout = 30

# Worker temp directory
worker_tmp_dir = "/dev/shm"

# Limit request line and header field sizes
limit_request_line = 4094
limit_request_fields = 100
limit_request_field_size = 8190

# Security
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'ssl',
    'X-FORWARDED-SSL': 'on'
}

# Environment variables for production
raw_env = [
    'ENVIRONMENT=production',
    'WORKERS=4',
    'MAX_REQUESTS=1000'
]

# Hook functions
def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)

def pre_exec(server):
    server.log.info("Forked child, re-executing.")

def when_ready(server):
    server.log.info("Server is ready. Starting to serve.")

def worker_int(worker):
    worker.log.info("worker received INT or QUIT signal")

def worker_abort(worker):
    worker.log.info("worker aborted (oom, timeout, etc)")

# Metrics and monitoring
statsd_host = None
statsd_prefix = ""

# Max requests per worker
max_requests = 1000
max_requests_jitter = 50

# Worker connections
worker_connections = 1000

# Worker timeout
timeout = 30
graceful_timeout = 30

# Keep alive
keepalive = 2

# Server mechanics
daemon = False
pidfile = "./gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# Logging configuration
def on_starting(server):
    """Called just before the master process is initialized."""
    server.log.info("Starting Postify backend server...")

def on_reload(server):
    """Called to recycle workers during a reload via SIGHUP."""
    server.log.info("Reloading Postify backend server...")

def worker_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Worker exited (pid: %s)", worker.pid)

def child_exit(server, worker):
    """Called just after a worker has been exited."""
    server.log.info("Child worker exited (pid: %s)", worker.pid)

def pre_request(worker, req):
    """Called just before a worker processes the request."""
    worker.log.info("Worker %s processing request: %s %s", worker.pid, req.method, req.path)

def post_request(worker, req, environ, resp):
    """Called after a worker processes the request."""
    worker.log.info("Worker %s completed request: %s %s - Status: %s", 
                   worker.pid, req.method, req.path, resp.status)
