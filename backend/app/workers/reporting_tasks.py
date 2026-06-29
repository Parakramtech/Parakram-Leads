"""Weekly reporting tasks for Sigma Lead Intelligence."""
import logging
from datetime import datetime, timedelta

from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.lead import Lead, LeadCategory, LeadStatus
from app.models.message import Message
from app.models.organization import Organization, OrgRole, UserOrganization
from app.models.user import User
from app.workers.celery_app import celery_app, run_async

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=2, default_retry_delay=60)
def generate_weekly_report_task(self) -> dict:
    """Generate and send weekly digest report for all active organizations."""
    try:
        engine = create_engine(settings.DATABASE_URL_SYNC)
        SessionLocal = sessionmaker(bind=engine)

        reports_sent = 0
        week_ago = datetime.utcnow() - timedelta(days=7)

        with SessionLocal() as db:
            # Get all active organizations
            orgs = db.query(Organization).filter(
                Organization.is_active == True
            ).all()

            for org in orgs:
                # Gather weekly stats
                new_leads = db.query(func.count(Lead.id)).filter(
                    Lead.organization_id == org.id,
                    Lead.created_at >= week_ago,
                ).scalar() or 0

                hot_leads = db.query(func.count(Lead.id)).filter(
                    Lead.organization_id == org.id,
                    Lead.category_flag == LeadCategory.HOT,
                    Lead.created_at >= week_ago,
                ).scalar() or 0

                messages_sent = db.query(func.count(Message.id)).filter(
                    Message.organization_id == org.id,
                    Message.sent_at >= week_ago,
                ).scalar() or 0

                responses = db.query(func.count(Message.id)).filter(
                    Message.organization_id == org.id,
                    Message.replied_at >= week_ago,
                ).scalar() or 0

                pipeline_value = db.query(
                    func.sum(Lead.estimated_project_value)
                ).filter(
                    Lead.organization_id == org.id,
                    Lead.category_flag.in_([LeadCategory.HOT, LeadCategory.WARM]),
                    Lead.status != LeadStatus.DISQUALIFIED,
                ).scalar() or 0

                # Build report summary
                report = {
                    "org_name": org.name,
                    "period": (
                        f"{week_ago.strftime('%b %d')} - "
                        f"{datetime.utcnow().strftime('%b %d, %Y')}"
                    ),
                    "new_leads": new_leads,
                    "hot_leads": hot_leads,
                    "messages_sent": messages_sent,
                    "responses": responses,
                    "response_rate": (
                        f"{(responses / messages_sent * 100):.1f}%"
                        if messages_sent > 0
                        else "0%"
                    ),
                    "pipeline_value": pipeline_value,
                }

                # Send email report (uses email service if available)
                try:
                    from app.services.email_service import get_email_provider

                    provider = get_email_provider()
                    subject = (
                        f"Weekly Report: {org.name} - {report['period']}"
                    )
                    html_body = _build_report_html(report)

                    # Send to org admin (first admin user)
                    admin = db.query(UserOrganization).filter(
                        UserOrganization.organization_id == org.id,
                        UserOrganization.role == OrgRole.ADMIN,
                    ).first()

                    if admin:
                        user = db.query(User).filter(
                            User.id == admin.user_id
                        ).first()
                        if user and user.email:
                            run_async(
                                provider.send(user.email, subject, html_body)
                            )
                            reports_sent += 1
                except ImportError:
                    logger.info(
                        "Email service not available; logging report for "
                        "org %s: %s",
                        org.name,
                        report,
                    )
                except Exception as e:
                    logger.warning(
                        "Failed to send report for org %s: %s", org.name, e
                    )

        return {"status": "completed", "reports_sent": reports_sent}
    except Exception as e:
        logger.error("Weekly report task failed: %s", e)
        raise self.retry(exc=e)


def _build_report_html(report: dict) -> str:
    """Build HTML email body for weekly report."""
    return f"""
    <html>
    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h1 style="color: #1a1a2e;">Weekly Intelligence Report</h1>
        <p style="color: #666;">{report['org_name']} | {report['period']}</p>

        <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2 style="margin-top: 0;">Key Metrics</h2>
            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 8px 0;"><strong>New Leads Discovered</strong></td>
                    <td style="text-align: right;">{report['new_leads']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Hot Leads</strong></td>
                    <td style="text-align: right; color: #e63946;">{report['hot_leads']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Messages Sent</strong></td>
                    <td style="text-align: right;">{report['messages_sent']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Responses Received</strong></td>
                    <td style="text-align: right;">{report['responses']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Response Rate</strong></td>
                    <td style="text-align: right;">{report['response_rate']}</td>
                </tr>
                <tr>
                    <td style="padding: 8px 0;"><strong>Pipeline Value</strong></td>
                    <td style="text-align: right; color: #2a9d8f;">₹{report['pipeline_value']:,.0f}</td>
                </tr>
            </table>
        </div>

        <p style="color: #666; font-size: 12px;">
            This is an automated report from Sigma Lead Intelligence.
        </p>
    </body>
    </html>
    """
