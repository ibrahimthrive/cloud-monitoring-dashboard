"""REST API for system metrics, processes, services, and alerts."""
import logging
from datetime import datetime, timedelta
from functools import wraps

from flask import jsonify, request
from flask_login import login_required, current_user

from app.api import api_bp
from app.extensions import db
from app.models import MetricSnapshot, AlertLog
from app.monitoring import metrics as metrics_module
from app.monitoring.alerts import get_or_create_settings

logger = logging.getLogger(__name__)


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({"error": "Admin privileges required"}), 403
        return fn(*args, **kwargs)

    return wrapper


@api_bp.route("/metrics/current")
@login_required
def metrics_current():
    return jsonify(metrics_module.get_current_metrics())


@api_bp.route("/metrics/history")
@login_required
def metrics_history():
    hours = request.args.get("hours", default=1, type=float)
    hours = max(0.1, min(hours, 24 * 7))
    cutoff = datetime.utcnow() - timedelta(hours=hours)

    snapshots = (
        MetricSnapshot.query.filter(MetricSnapshot.timestamp >= cutoff)
        .order_by(MetricSnapshot.timestamp.asc())
        .all()
    )
    return jsonify([s.to_dict() for s in snapshots])


@api_bp.route("/processes")
@login_required
def processes():
    limit = request.args.get("limit", default=50, type=int)
    sort_by = request.args.get("sort_by", default="cpu_percent")
    if sort_by not in ("cpu_percent", "memory_percent", "pid", "name"):
        sort_by = "cpu_percent"
    return jsonify(metrics_module.get_processes(limit=min(limit, 200), sort_by=sort_by))


@api_bp.route("/services")
@login_required
def services():
    return jsonify(metrics_module.get_services())


@api_bp.route("/uptime")
@login_required
def uptime():
    return jsonify(
        {
            "uptime_seconds": metrics_module.get_uptime_seconds(),
            "uptime_human": metrics_module.get_uptime_human(),
        }
    )


@api_bp.route("/alerts/settings", methods=["GET"])
@login_required
def get_alert_settings():
    return jsonify(get_or_create_settings().to_dict())


@api_bp.route("/alerts/settings", methods=["POST"])
@login_required
@admin_required
def update_alert_settings():
    payload = request.get_json(silent=True) or {}
    settings = get_or_create_settings()

    for field in ("cpu_threshold", "ram_threshold", "disk_threshold"):
        if field in payload:
            try:
                value = float(payload[field])
            except (TypeError, ValueError):
                return jsonify({"error": f"Invalid value for {field}"}), 400
            if not 0 <= value <= 100:
                return jsonify({"error": f"{field} must be between 0 and 100"}), 400
            setattr(settings, field, value)

    if "email_enabled" in payload:
        settings.email_enabled = bool(payload["email_enabled"])

    db.session.commit()
    logger.info("Alert settings updated by %s: %s", current_user.username, settings.to_dict())
    return jsonify(settings.to_dict())


@api_bp.route("/alerts/logs")
@login_required
def alert_logs():
    limit = min(request.args.get("limit", default=50, type=int), 200)
    logs = AlertLog.query.order_by(AlertLog.timestamp.desc()).limit(limit).all()
    return jsonify([log.to_dict() for log in logs])
