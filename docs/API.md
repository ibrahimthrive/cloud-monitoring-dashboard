# REST API Reference

All endpoints (except `/auth/*`) require an authenticated session cookie. Sign in via `POST /auth/login` first (the browser handles this automatically through the login form).

State-changing requests (`POST`) require a CSRF token, sent as the `X-CSRFToken` header. The token is rendered into a `<meta name="csrf-token">` tag on every page; the bundled `static/js/api.js` helper attaches it automatically.

Base URL: `/api`

## GET /api/metrics/current

Live snapshot of CPU, RAM, disk, network, and uptime. Polled by the dashboard every `LIVE_REFRESH_INTERVAL_SECONDS` (default 5s).

**Response 200**
```json
{
  "timestamp": "2026-06-27T10:15:00.123456",
  "cpu": { "percent": 12.5, "per_core": [10.0, 15.0], "core_count": 8, "physical_cores": 4, "load_avg": [0.5, 0.4, 0.3] },
  "ram": { "percent": 42.1, "used_mb": 6800.5, "total_mb": 16000.0, "available_mb": 9200.0 },
  "disk": { "percent": 55.3, "used_gb": 120.4, "total_gb": 256.0, "free_gb": 135.6 },
  "network": { "upload_kbps": 12.3, "download_kbps": 88.1, "total_sent_mb": 1024.5, "total_recv_mb": 8192.2 },
  "uptime_seconds": 86412,
  "uptime_human": "1d 0h 0m",
  "hostname": "prod-server-01",
  "os": "Linux 6.8.0"
}
```

## GET /api/metrics/history?hours=1

Historical metrics persisted to SQLite by the background collector. `hours` accepts 0.1–168 (default 1).

**Response 200** — array of stored snapshots, oldest first:
```json
[
  { "timestamp": "...", "cpu_percent": 10.2, "ram_percent": 40.1, "ram_used_mb": 6500.0, "ram_total_mb": 16000.0,
    "disk_percent": 55.0, "disk_used_gb": 120.0, "disk_total_gb": 256.0, "net_sent_kbps": 10.0, "net_recv_kbps": 50.0 }
]
```

## GET /api/processes?limit=50&sort_by=cpu_percent

Running processes, sorted descending. `sort_by` is one of `cpu_percent`, `memory_percent`, `pid`, `name`. `limit` is capped at 200.

## GET /api/services

Best-effort list of OS services. Uses `psutil.win_service_iter()` on Windows and `systemctl list-units --type=service` on Linux. Returns `[]` where neither is available (e.g. minimal containers).

## GET /api/uptime

```json
{ "uptime_seconds": 86412, "uptime_human": "1d 0h 0m" }
```

## GET /api/alerts/settings

Returns the active alert thresholds:
```json
{ "cpu_threshold": 85.0, "ram_threshold": 85.0, "disk_threshold": 90.0, "email_enabled": false }
```

## POST /api/alerts/settings

**Admin only.** Body (all fields optional):
```json
{ "cpu_threshold": 80, "ram_threshold": 80, "disk_threshold": 90, "email_enabled": true }
```
Returns `400` if a threshold is outside `0–100`, or `403` if the caller is not an admin.

## GET /api/alerts/logs?limit=50

Most recent alerts (threshold breaches), newest first. `limit` capped at 200.
```json
[
  { "timestamp": "...", "metric_type": "cpu", "value": 91.2, "threshold": 85.0,
    "message": "CPU usage at 91.2% exceeds threshold of 85.0%", "email_sent": true }
]
```

## Error format

Errors return JSON with an `error` key and an appropriate HTTP status code (`400`, `403`, `404`, `500`).
