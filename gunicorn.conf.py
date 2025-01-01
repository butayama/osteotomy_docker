# Gunicorn configuration file.

# Server socket
bind = '0.0.0.0:8000'  # Listen on all interfaces at port 8000
backlog = 2048

# Worker processes
workers = 2  # Adjust based on server's available CPU cores
worker_class = 'sync'
worker_connections = 1000
timeout = 30
keepalive = 2

# Debugging/verbose logging
spew = False

# Server mechanics
daemon = False
pidfile = None
umask = 0
user = None
group = None
tmp_upload_dir = None

# Logging
errorlog = '-'
loglevel = 'info'
accesslog = '-'
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# SSL configuration (disabled)
# Removed SSL options, as TLS is handled through Nginx
# certfile = '/ssl/certs/chain_123.crt'
# keyfile = '/ssl/certs/osteotomy.eu.key'

# Process naming
proc_name = None


# Hooks
def post_fork(server, worker):
    server.log.info("Worker spawned (pid: %s)", worker.pid)


def pre_fork(server, worker):
    pass


def pre_exec(server):
    server.log.info("Forked child, re-executing.")


def when_ready(server):
    server.log.info("Server is ready. Spawning workers")


def worker_abort(worker):
    worker.log.info("Worker received SIGABRT signal")
