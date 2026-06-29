from fastapi import APIRouter, Depends, Request, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.config import settings
from app.models.message import Message, MessageStatus
from app.models.lead import Lead
from app.services.alerter import send_personal_alert
from datetime import datetime
from uuid import UUID
from typing import Optional

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


async def verify_webhook_secret(x_webhook_secret: Optional[str] = Header(None, alias="x-webhook-secret")):
    if not settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Webhook processing not configured")
    if not x_webhook_secret or x_webhook_secret != settings.WEBHOOK_SECRET:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True


@router.post("/email-status")
async def email_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_webhook_secret),
):
    data = await request.json()
    event = data.get("event", "")
    external_id = data.get("message_id", "")
    if not external_id:
        return {"status": "ignored"}
    result = await db.execute(select(Message).where(Message.external_id == external_id))
    message = result.scalar_one_or_none()
    if not message:
        return {"status": "not_found"}
    if event == "delivered":
        message.status = MessageStatus.DELIVERED
        message.delivered_at = datetime.utcnow()
    elif event == "opened":
        message.status = MessageStatus.OPENED
        message.opened_at = datetime.utcnow()
    return {"status": "ok"}


@router.post("/whatsapp")
async def whatsapp_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_webhook_secret),
):
    data = await request.json()
    messages = data.get("messages", [])
    for msg in messages:
        from_number = msg.get("from", "")
        text = msg.get("text", {}).get("body", "")
        msg_id = msg.get("id", "")
        if not from_number:
            continue
        result = await db.execute(
            select(Message).where(Message.external_id == from_number)
        )
        message = result.scalar_one_or_none()
        if not message:
            continue
        message.status = MessageStatus.REPLIED
        message.replied_at = datetime.utcnow()
        message.reply_content = text
        lead_result = await db.execute(select(Lead).where(Lead.id == message.lead_id))
        lead = lead_result.scalar_one_or_none()
        if lead:
            lead.response_received = True
            lead.response_text = text
            lead.response_received_at = datetime.utcnow()
            await send_personal_alert(lead, text)
    return {"status": "ok"}


@router.post("/whatsapp-inbound")
async def whatsapp_bridge_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: bool = Depends(verify_webhook_secret),
):
    data = await request.json()
    from_number = data.get("from", "")
    text = data.get("message", "")
    msg_id = data.get("message_id", "")

    if not from_number or not text:
        return {"status": "ignored"}

    result = await db.execute(
        select(Message).where(Message.external_id == from_number)
    )
    message = result.scalar_one_or_none()
    if not message:
        return {"status": "not_found"}

    message.status = MessageStatus.REPLIED
    message.replied_at = datetime.utcnow()
    message.reply_content = text

    lead_result = await db.execute(select(Lead).where(Lead.id == message.lead_id))
    lead = lead_result.scalar_one_or_none()
    if lead:
        lead.response_received = True
        lead.response_text = text
        lead.response_received_at = datetime.utcnow()
        await send_personal_alert(lead, text)

    return {"status": "ok"}
