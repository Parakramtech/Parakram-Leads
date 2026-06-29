from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery_app = Celery(
    "sigma_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.collection_tasks",
        "app.workers.outreach_tasks",
        "app.workers.scoring_tasks",
        "app.workers.reporting_tasks",
        "app.workers.intelligence_tasks",
        "agents.tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_time_limit=300,
    task_soft_time_limit=280,
    beat_schedule={
        "daily-auto-analyze": {
            "task": "app.workers.collection_tasks.batch_analyze_leads_task",
            "schedule": crontab(hour=2, minute=0),
            "args": (100,),
        },
        "weekly-digest": {
            "task": "app.workers.reporting_tasks.generate_weekly_report_task",
            "schedule": crontab(day_of_week=1, hour=8, minute=0),
        },
        "daily-retention-check": {
            "task": "app.workers.retention_tasks.enforce_retention_task",
            "schedule": crontab(hour=3, minute=0),
        },
        "intelligence-batch-scan": {
            "task": "app.workers.intelligence_tasks.batch_intelligence_scan_task",
            "schedule": crontab(hour=0, minute=30),
            "args": (100,),
        },
        "buying-signal-check": {
            "task": "app.workers.intelligence_tasks.batch_intelligence_scan_task",
            "schedule": crontab(hour="*/6", minute=15),
            "args": (50,),
        },
        "parakram-growth-agent": {
            "task": "agents.tasks.run_growth_agent_cycle",
            "schedule": crontab(hour="*/8", minute=30),
            "args": ("Bangalore", 30),
        },
    },
)
