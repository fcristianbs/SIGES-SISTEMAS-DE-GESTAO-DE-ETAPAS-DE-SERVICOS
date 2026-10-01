import multiprocessing
import os

# Configurações do Servidor Gunicorn para VPS Produção
bind = os.getenv("GUNICORN_BIND", "127.0.0.1:8000")

# Quantidade de workers: (2 * núcleos de CPU) + 1, com mínimo de 2 e padrão 4
cores = multiprocessing.cpu_count()
workers = int(os.getenv("GUNICORN_WORKERS", max(2, min(4, 2 * cores + 1))))
threads = int(os.getenv("GUNICORN_THREADS", 2))
worker_class = "gthread"

# Timeouts e conexões
timeout = int(os.getenv("GUNICORN_TIMEOUT", 120))
keepalive = 5
max_requests = 1000
max_requests_jitter = 50

# Logs estruturados no console (coletados pelo Systemd / Journald)
accesslog = "-"
errorlog = "-"
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)sµs'

# Otimizações de processo
preload_app = False
proc_name = "siges_wsgi"
