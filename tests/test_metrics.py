from app.monitoring import metrics


def test_get_cpu_metrics_returns_percent():
    data = metrics.get_cpu_metrics()
    assert 0 <= data["percent"] <= 100
    assert data["core_count"] >= 1


def test_get_ram_metrics_returns_percent():
    data = metrics.get_ram_metrics()
    assert 0 <= data["percent"] <= 100
    assert data["total_mb"] > 0


def test_get_disk_metrics_returns_percent():
    data = metrics.get_disk_metrics()
    assert 0 <= data["percent"] <= 100
    assert data["total_gb"] > 0


def test_get_network_metrics_returns_non_negative():
    data = metrics.get_network_metrics()
    assert data["upload_kbps"] >= 0
    assert data["download_kbps"] >= 0


def test_get_uptime_seconds_positive():
    assert metrics.get_uptime_seconds() >= 0


def test_get_processes_respects_limit():
    processes = metrics.get_processes(limit=3)
    assert len(processes) <= 3


def test_get_current_metrics_has_all_sections():
    data = metrics.get_current_metrics()
    for key in ("cpu", "ram", "disk", "network", "uptime_seconds", "uptime_human", "hostname", "os"):
        assert key in data
