from app.models import AlertLog
from app.monitoring.alerts import check_thresholds


def test_check_thresholds_creates_alert_when_exceeded(app):
    with app.app_context():
        triggered = check_thresholds(cpu_percent=99.0, ram_percent=10.0, disk_percent=10.0)
        assert len(triggered) == 1
        assert triggered[0].metric_type == "cpu"
        assert AlertLog.query.count() == 1


def test_check_thresholds_respects_cooldown(app):
    with app.app_context():
        first = check_thresholds(cpu_percent=99.0, ram_percent=10.0, disk_percent=10.0)
        second = check_thresholds(cpu_percent=99.0, ram_percent=10.0, disk_percent=10.0)
        assert len(first) == 1
        assert len(second) == 0
        assert AlertLog.query.count() == 1


def test_check_thresholds_no_alert_below_threshold(app):
    with app.app_context():
        triggered = check_thresholds(cpu_percent=10.0, ram_percent=10.0, disk_percent=10.0)
        assert triggered == []
        assert AlertLog.query.count() == 0
