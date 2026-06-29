"""Celery tasks for the Parakram Growth Agent — runs autonomously on a schedule."""

import logging
from app.workers.celery_app import app, run_async
from agents.parakram_growth_agent import run_acquisition_cycle

logger = logging.getLogger(__name__)


@app.task(bind=True, max_retries=3, soft_time_limit=600, time_limit=660)
def run_growth_agent_cycle(self, location: str = "Bangalore", max_leads: int = 30):
    """Run one acquisition cycle for Parakram's own customer growth."""
    try:
        result = run_async(run_acquisition_cycle(location=location, max_leads=max_leads))
        logger.info(f"Growth agent cycle complete: {result}")
        return result
    except Exception as exc:
        logger.error(f"Growth agent cycle failed: {exc}")
        raise self.retry(exc=exc, countdown=300)
