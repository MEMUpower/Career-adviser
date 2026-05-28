from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "career_advisor_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Seoul",
    enable_utc=False,
)

# Automated ETL Scheduler Setup (Runs every midnight KST)
celery_app.conf.beat_schedule = {
    "collect-public-metrics-daily": {
        "task": "app.tasks.etl_tasks.run_public_metrics_etl",
        "schedule": crontab(hour=0, minute=0),
    }
}

celery_app.autodiscover_tasks([
    "app.tasks.document_tasks",
    "app.tasks.etl_tasks",
    "app.tasks.report_tasks"
])
