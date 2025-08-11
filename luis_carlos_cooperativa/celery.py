import os
import warnings
from celery import Celery
from celery.platforms import SecurityWarning


warnings.filterwarnings("ignore", category=SecurityWarning)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'luis_carlos_cooperativa.settings')

app = Celery('luis_carlos_cooperativa')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
