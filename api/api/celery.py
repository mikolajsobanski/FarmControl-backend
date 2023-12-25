import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'api.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('api',backend='db+postgresql://postgres:postgres@localhost:5432/farmControl', broker='pyamqp://guest@localhost//')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'test-task': {
        'task':  'apianalysis.tasks.check_vaccine_expiry',  
        'schedule': crontab(hour=20, minute=40),  
    },
}
app.conf.timezone = 'UTC'
