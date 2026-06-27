def test_metrics_current_requires_login(client):
    response = client.get("/api/metrics/current")
    assert response.status_code in (302, 401)


def test_metrics_current_returns_expected_keys(login):
    response = login.get("/api/metrics/current")
    assert response.status_code == 200
    data = response.get_json()
    for key in ("cpu", "ram", "disk", "network", "uptime_seconds", "hostname"):
        assert key in data
    assert "percent" in data["cpu"]
    assert "percent" in data["ram"]


def test_processes_endpoint(login):
    response = login.get("/api/processes?limit=5")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) <= 5


def test_services_endpoint(login):
    response = login.get("/api/services")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)


def test_uptime_endpoint(login):
    response = login.get("/api/uptime")
    assert response.status_code == 200
    data = response.get_json()
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


def test_alert_settings_get_and_update(login):
    response = login.get("/api/alerts/settings")
    assert response.status_code == 200

    response = login.post(
        "/api/alerts/settings",
        json={"cpu_threshold": 75, "ram_threshold": 80, "disk_threshold": 95, "email_enabled": False},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["cpu_threshold"] == 75
    assert data["ram_threshold"] == 80


def test_alert_settings_rejects_invalid_value(login):
    response = login.post("/api/alerts/settings", json={"cpu_threshold": 150})
    assert response.status_code == 400


def test_metrics_history_returns_list(login):
    response = login.get("/api/metrics/history?hours=1")
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)
