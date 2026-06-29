import smtplib
import ssl
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import settings
from app.models.lead import Lead
from app.models.message import Message, MessageChannel, MessageStatus
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


async def send_email(lead: Lead, message: Message, db: AsyncSession) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD]):
        return False
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_FROM
        msg["To"] = lead.email
        msg["Subject"] = message.content.split("\n")[0] if message.content.startswith("Subject:") else f"Hello from Sigma"

        body = message.content
        if body.startswith("Subject:"):
            lines = body.split("\n", 1)
            body = lines[1] if len(lines) > 1 else body

        msg.attach(MIMEText(body, "plain"))

        context = ssl.create_default_context()
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM, lead.email, msg.as_string())

        message.status = MessageStatus.SENT
        message.sent_at = datetime.now(timezone.utc)
        await db.flush()
        return True
    except Exception as e:
        message.status = MessageStatus.FAILED
        await db.flush()
        return False


async def send_whatsapp_bridge(lead: Lead, message: Message, db: AsyncSession) -> bool:
    if not settings.WHATSAPP_BRIDGE_URL or not lead.phone:
        return False
    try:
        import httpx
        url = f"{settings.WHATSAPP_BRIDGE_URL}/send"
        payload = {"to": lead.phone, "message": message.content}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(url, json=payload)
            if resp.status_code in (200, 201):
                data = resp.json()
                message.external_id = data.get("id", "")
                message.status = MessageStatus.SENT
                message.sent_at = datetime.now(timezone.utc)
                await db.flush()
                return True
    except Exception as e:
        logger.exception("WhatsApp bridge send failed")
    message.status = MessageStatus.FAILED
    await db.flush()
    return False


async def send_whatsapp(lead: Lead, message: Message, db: AsyncSession) -> bool:
    if all([settings.WHATSAPP_API_KEY, settings.WHATSAPP_PHONE_NUMBER_ID]):
        try:
            import httpx
            url = f"https://graph.facebook.com/v18.0/{settings.WHATSAPP_PHONE_NUMBER_ID}/messages"
            headers = {
                "Authorization": f"Bearer {settings.WHATSAPP_API_KEY}",
                "Content-Type": "application/json",
            }
            payload = {
                "messaging_product": "whatsapp",
                "to": lead.phone,
                "type": "text",
                "text": {"body": message.content},
            }
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.post(url, json=payload, headers=headers)
                if resp.status_code in (200, 201):
                    data = resp.json()
                    message.external_id = data.get("messages", [{}])[0].get("id", "")
                    message.status = MessageStatus.SENT
                    message.sent_at = datetime.now(timezone.utc)
                    await db.flush()
                    return True
        except Exception as e:
            logger.exception("WhatsApp API send failed")
        message.status = MessageStatus.FAILED
        await db.flush()
        return False
    return await send_whatsapp_bridge(lead, message, db)


async def send_message(lead: Lead, channel: MessageChannel, content: str, db: AsyncSession) -> Message:
    message = Message(
        lead_id=lead.id,
        channel=channel,
        content=content,
        status=MessageStatus.DRAFT,
    )
    db.add(message)
    await db.flush()

    if channel == MessageChannel.EMAIL:
        success = await send_email(lead, message, db)
    elif channel == MessageChannel.WHATSAPP:
        success = await send_whatsapp(lead, message, db)
    else:
        message.status = MessageStatus.DRAFT

    await db.refresh(message)
    return message
