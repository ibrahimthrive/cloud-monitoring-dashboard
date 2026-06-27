"""Background job: periodically persists a metrics snapshot and evaluates alerts."""
import logging
from datetime import datetime, timedelta

from app.extensions import db
from app.models import MetricSnapshot
from app.monitoring import metrics as metrics_module
from app.monitoring.alerts import check_thresholds

logger = logging.getLogger(__name__)


def collect_and_store(app):
    """Runs inside the app context on a schedule; safe to call directly in tests."""
    with app.app_context():
        try:
            cpu = metrics_module.get_cpu_metrics()
            ram = metrics_module.get_ram_metrics()
            disk = metrics_module.get_disk_metrics()
            network = metrics_module.get_network_metrics()

            snapshot = MetricSnapshot(
                cpu_percent=cpu["percent"],
                ram_percent=ram["percent"],
                ram_used_mb=ram["used_mb"],
                ram_total_mb=ram["total_mb"],
                disk_percent=disk["percent"],
                disk_used_gb=disk["used_gb"],
                disk_total_gb=disk["total_gb"],
                net_sent_kbps=network["upload_kbps"],
                net_recv_kbps=network["download_kbps"],
            )
            db.session.add(snapshot)
            db.session.commit()

            check_thresholds(cpu["percent"], ram["percent"], disk["percent"])
            _prune_old_snapshots(app)
        except Exception:
            logger.exception("Metrics collection cycle failed")
            db.session.rollback()


def _prune_old_snapshots(app):
    retention_days = app.config["METRICS_RETENTION_DAYS"]
    cutoff = datetime.utcnow() - timedelta(days=retention_days)
    MetricSnapshot.query.filter(MetricSnapshot.timestamp < cutoff).delete()
    db.session.commit()


def init_scheduler(app, scheduler):
    if not app.config.get("SCHEDULER_ENABLED", True):
        return

    interval = app.config["METRICS_COLLECTION_INTERVAL_SECONDS"]
    scheduler.add_job(
        func=lambda: collect_and_store(app),
        trigger="interval",
        seconds=interval,
        id="metrics_collector",
        replace_existing=True,
        max_instances=1,
    )
    if not scheduler.running:
        scheduler.start()
    logger.info("Metrics collector scheduled every %ss", interval)
