import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bittrade.settings')
app = Celery('bittrade')

app.conf.broker_url = 'redis://redis_channel:6379/0'
app.conf.result_backend = 'redis://redis_channel:6379/0'

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
