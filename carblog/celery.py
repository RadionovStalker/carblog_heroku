from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.apps import apps
from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'carblog.settings')

app = Celery('carblog')
app.config_from_object(settings)
# app.autodiscover_tasks()
app.autodiscover_tasks(settings.INSTALLED_APPS)


app.conf.beat_schedule = {
    'add-every-1-seconds': {
        'task': 'blog_engine.tasks.add',
        'schedule': 1.0,
        'args': (3, 4)
    },
}
