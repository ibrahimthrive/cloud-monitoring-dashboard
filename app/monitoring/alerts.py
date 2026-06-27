"""Threshold-based alerting on top of collected metrics."""
import logging
from datetime import datetime, timedelta

from flask import current_app

from app.extensions import db
from app.models import AlertLog, AlertSettings
from app.monitoring.email_notifications import send_alert_email

logger = logging.getLogger(__name__)

_last_alert_sent = {}  # metric_type -> datetime, per-process cooldown tracker


def get_or_create_settings():
    settings = AlertSettings.query.first()
    if settings is None:
        settings = AlertSettings(
            cpu_threshold=current_app.config["DEFAULT_CPU_ALERT_THRESHOLD"],
            ram_threshold=current_app.config["DEFAULT_RAM_ALERT_THRESHOLD"],
            disk_threshold=current_app.config["DEFAULT_DISK_ALERT_THRESHOLD"],
            email_enabled=current_app.config["MAIL_ENABLED"],
        )
        db.session.add(settings)
        db.session.commit()
    return settings


def reset_cooldowns():
    """Clears in-memory cooldown tracking. Used by tests and on app restart."""
    _last_alert_sent.clear()


def _cooldown_elapsed(metric_type):
    cooldown = timedelta(seconds=current_app.config["ALERT_COOLDOWN_SECONDS"])
    last = _last_alert_sent.get(metric_type)
    return last is None or (datetime.utcnow() - last) >= cooldown


def _record_alert(metric_type, value, threshold, settings):
    message = f"{metric_type.upper()} usage at {value:.1f}% exceeds threshold of {threshold:.1f}%"
    email_sent = False

    if settings.email_enabled:
        email_sent = send_alert_email(
            subject=f"[ALERT] High {metric_type.upper()} usage",
            body=message,
        )

    alert = AlertLog(
        metric_type=metric_type,
        value=value,
        threshold=threshold,
        message=message,
        email_sent=email_sent,
    )
    db.session.add(alert)
    db.session.commit()
    _last_alert_sent[metric_type] = datetime.utcnow()
    logger.warning("ALERT: %s", message)
    return alert


def check_thresholds(cpu_percent, ram_percent, disk_percent):
    """Evaluate metrics against configured thresholds and raise alerts as needed."""
    settings = get_or_create_settings()
    triggered = []

    checks = (
        ("cpu", cpu_percent, settings.cpu_threshold),
        ("ram", ram_percent, settings.ram_threshold),
        ("disk", disk_percent, settings.disk_threshold),
    )

    for metric_type, value, threshold in checks:
        if value >= threshold and _cooldown_elapsed(metric_type):
            triggered.append(_record_alert(metric_type, value, threshold, settings))

    return triggered
