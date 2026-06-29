from app.models.lead import Lead
from app.models.message import Message, MessageChannel
from app.services.alerter import send_personal_alert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timezone


async def process_response(lead: Lead, channel: str, content: str, db: AsyncSession):
    lead.response_received = True
    lead.response_text = content
    lead.response_received_at = datetime.now(timezone.utc)
    await db.flush()

    result = await db.execute(
        select(Message).where(
            Message.lead_id == lead.id,
            Message.channel == channel,
        ).order_by(Message.created_at.desc()).limit(1)
    )
    message = result.scalar_one_or_none()
    if message:
        message.status = "replied"
        message.replied_at = datetime.now(timezone.utc)
        message.reply_content = content
        await db.flush()

    await send_personal_alert(lead, content)
