import multiprocessing
import os

# Configurações do Gunicorn
bind = "0.0.0.0:8000"

# Calcula o número de workers dinamicamente
# A regra geral é (2 * número de CPUs) + 1
workers = (multiprocessing.cpu_count() * 2) + 1
worker_class = "uvicorn.workers.UvicornWorker"

# Configurações de logging
loglevel = os.getenv("LOG_LEVEL", "info")
accesslog = "-"
errorlog = "-"
