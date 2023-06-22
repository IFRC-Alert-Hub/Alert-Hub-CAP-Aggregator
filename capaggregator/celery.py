import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from django.conf import settings
from dotenv import load_dotenv

# Load environment variables from .env file
if 'WEBSITE_HOSTNAME' not in os.environ:
    load_dotenv(".env")
    # Set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capaggregator.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'capaggregator.production')
app = Celery('capaggregator')

app.conf.beat_schedule = {
    'polling-alerts-from-feeds-at-1-min':{
        'task': 'cap_feed.tasks.getAlerts',
        'schedule': timedelta(minutes=1)
    }

}
# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object(settings, namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')