""" gunicorn WSGI server configuration. """

from multiprocessing import cpu_count
from os import environ


def max_workers():
    # Gunicorn suggests (1-4 x $CORES) + 1
    # We can tweak this if we need.
    return (cpu_count() * 2) + 1


bind = '0.0.0.0:' + environ.get('PORT', '8080')

workers = max_workers()
worker_class = 'gevent'  # 'sync'
worker_connections = 1000  # Max active connections at any one time

backlog = 2048  # Max queued connections at any one time
max_requests = 1000  # Recycle each worker after N requests
timeout = 25  # Kill requests after N seconds
