from celery import Celery
from celery.schedules import crontab
import os



celery = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery.conf.task_routes = {
    "tasks.*": {"queue": "default"},
}

celery.conf.beat_schedule = {
    'check-sheet-updates-every-minute': {
        'task': 'core.tasks.check_sheet_updates',
        'schedule': crontab(minute='*'),
    },
}

celery.autodiscover_tasks(["core.tasks"], related_name=None)