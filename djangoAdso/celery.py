import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "djangoAdso.settings")  # change if needed
app = Celery("djangoAdso")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

app.conf.beat_schedule = {
    "check-evolution-every-15-min": {
        "task": "core.tasks.check_evolution_and_notify",
        "schedule": crontab(minute="*/15"),
    },
}