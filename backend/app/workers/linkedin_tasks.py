"""Celery tasks for LinkedIn outreach."""
import logging
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.workers.celery_app import celery_app
from app.config import settings
from app.workers.celery_app import run_async

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=300)
def send_linkedin_message_task(self, lead_id: str) -> dict:
    """Send a LinkedIn message to a lead via browser automation.
    
    Args:
        lead_id: UUID of the lead to message
        
    Returns:
        dict with status and optional error message
    """
    try:
        engine = create_engine(settings.DATABASE_URL_SYNC)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as db:
            from app.models.lead import Lead
            
            lead = db.query(Lead).filter(Lead.id == lead_id).first()
            if not lead:
                return {"status": "failed", "error": "lead_not_found"}
            
            # Check if lead has LinkedIn profile
            social_profiles = lead.social_profiles or {}
            linkedin_url = social_profiles.get("linkedin", "")
            
            if not linkedin_url:
                return {"status": "skipped", "reason": "no_linkedin_url"}
            
            # Get outreach message
            message_text = lead.outreach_message_linkedin
            if not message_text:
                return {"status": "skipped", "reason": "no_outreach_message"}
            
            # Check LinkedIn credentials
            if not settings.LINKEDIN_EMAIL or not settings.LINKEDIN_PASSWORD:
                return {"status": "skipped", "reason": "no_linkedin_credentials"}
            
            # Send via LinkedIn messenger
            success = run_async(_send_linkedin_async(linkedin_url, message_text))
            
            if success:
                lead.outreach_sent = True
                db.commit()
                return {"status": "sent", "lead_id": lead_id}
            else:
                return {"status": "failed", "error": "send_failed"}
                
    except Exception as e:
        logger.error(f"LinkedIn message task failed for lead {lead_id}: {e}")
        try:
            self.retry(exc=e)
        except self.MaxRetriesExceededError:
            return {"status": "failed", "error": str(e)}


async def _send_linkedin_async(profile_url: str, message_text: str) -> bool:
    """Async wrapper for LinkedIn messenger operations."""
    from app.services.linkedin_service import LinkedInMessenger
    
    messenger = LinkedInMessenger()
    try:
        logged_in = await messenger.login()
        if not logged_in:
            logger.error("LinkedIn login failed")
            return False
        
        success = await messenger.send_message(profile_url, message_text)
        return success
    finally:
        await messenger.close()
