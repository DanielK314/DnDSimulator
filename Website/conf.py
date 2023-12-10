import os
app_path = os.environ['HOME'] + '/git/DnDSimulator/Website'

# Gunicorn configuration
wsgi_app = 'fastAPITest:api'
bind = ':8000'
chdir = app_path
workers = 4
worker_class = 'uvicorn.workers.UvicornWorker'
errorlog =  app_path + '/errors.log'