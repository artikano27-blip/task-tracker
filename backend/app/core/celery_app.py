
from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

celery_app = Celery(
    "email_tasks",
    broker=settings.CELERY_BROKER_URL,
    include=["app.tasks.email"]
)

celery_app.conf.timezone = "Europe/Moscow"
celery_app.conf.beat_schedule = {
    "send-daily-summary-task": {
        "task": "app.tasks.email.dispatch_daily_summaries",
        "schedule": crontab(hour=0, minute=0),
    },
}

celery_app.conf.update(
    task_track_started=True,
)