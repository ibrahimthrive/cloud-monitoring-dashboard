"""Email notification helper built on Flask-Mail."""
import logging

from flask import current_app
from flask_mail import Message

from app.extensions import mail

logger = logging.getLogger(__name__)


def send_alert_email(subject, body, recipients=None):
    if not current_app.config.get("MAIL_ENABLED"):
        logger.debug("Mail disabled; skipping email send: %s", subject)
        return False

    recipients = recipients or current_app.config.get("ALERT_EMAIL_RECIPIENTS")
    if not recipients:
        logger.warning("No alert email recipients configured; skipping send")
        return False

    try:
        message = Message(subject=subject, recipients=recipients, body=body)
        mail.send(message)
        logger.info("Alert email sent to %s: %s", recipients, subject)
        return True
    except Exception:
        logger.exception("Failed to send alert email")
        return False
