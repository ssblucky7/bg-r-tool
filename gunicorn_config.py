bind = "0.0.0.0:$PORT"
workers = 2
threads = 4
timeout = 120
worker_class = "sync"
max_requests = 1000
max_requests_jitter = 50
