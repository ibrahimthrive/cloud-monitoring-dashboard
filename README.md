# Cloud Infrastructure Monitoring Dashboard

A production-ready Flask dashboard for monitoring server health in real time: CPU, RAM, disk, network throughput, running processes, services, and uptime — with historical charts, configurable threshold alerts, and email notifications.

## Features

- Session-based authentication (register/login/logout) with the first registered account auto-promoted to admin
- Live dashboard refreshing every 5 seconds via AJAX (CPU, RAM, disk, network up/down, uptime)
- Running processes and services tables (cross-platform: Windows services API / Linux `systemctl`)
- Historical metrics persisted to SQLite by a background collector (APScheduler), with automatic retention pruning
- Chart.js graphs: CPU/RAM history, network throughput, disk usage
- Configurable CPU/RAM/disk alert thresholds with cooldown-throttled alert log and optional email notifications (Flask-Mail)
- REST API covering every metric and the alerting system
- Dark/light theme toggle (persisted in `localStorage`)
- Responsive Bootstrap 5 UI
- Dockerfile + docker-compose, GitHub Actions CI (lint, test, Docker build), pytest unit tests
- Environment-variable-driven configuration, rotating file logging

## Project Structure

```
cloud-monitoring-dashboard/
├── app/
│   ├── __init__.py            # Application factory
│   ├── config.py               # Env-driven configuration
│   ├── extensions.py           # db, login_manager, mail, csrf, scheduler
│   ├── models.py                # User, MetricSnapshot, AlertSettings, AlertLog
│   ├── logging_config.py
│   ├── auth/                   # Login / register blueprint
│   ├── dashboard/               # HTML page routes
│   ├── api/                     # REST API blueprint
│   ├── monitoring/              # psutil metrics, alert engine, email, collector job
│   ├── static/{css,js}
│   └── templates/
├── tests/                       # pytest unit tests
├── docs/                        # API.md, deployment guides
├── .github/workflows/ci.yml
├── Dockerfile / docker-compose.yml
├── requirements.txt / requirements-dev.txt
├── run.py                       # Dev entrypoint (gunicorn used in Docker)
└── .env.example
```

## Quick Start (local)

```bash
python -m venv .venv
.venv\Scripts\activate            # Windows
# source .venv/bin/activate        # macOS/Linux

pip install -r requirements-dev.txt
copy .env.example .env             # Windows; cp on macOS/Linux, then edit values

python run.py
```

Visit `http://localhost:5000`, register an account (the first user becomes admin), and the dashboard starts polling live metrics immediately.

## Running with Docker

```bash
docker build -t cloud-monitoring-dashboard .
docker run -p 5000:5000 --env-file .env cloud-monitoring-dashboard
```

or with docker-compose (persists the SQLite DB and logs in named volumes):

```bash
docker compose up --build
```

**Note:** inside a container, `psutil` reports the container's own CPU/RAM/disk limits, not the host machine's, and the Linux service listing depends on `systemctl` being present. To monitor the underlying host from inside Docker, run the container with host networking/PID namespaces, or run the app directly on the host instead.

## Running tests

```bash
pip install -r requirements-dev.txt
pytest --cov=app
```

## Configuration

All configuration is via environment variables — see [`.env.example`](.env.example) for the full list, including:

- `SECRET_KEY`, `DATABASE_URL`
- `METRICS_COLLECTION_INTERVAL_SECONDS`, `METRICS_RETENTION_DAYS`, `LIVE_REFRESH_INTERVAL_SECONDS`
- `DEFAULT_CPU_ALERT_THRESHOLD`, `DEFAULT_RAM_ALERT_THRESHOLD`, `DEFAULT_DISK_ALERT_THRESHOLD`, `ALERT_COOLDOWN_SECONDS`
- `MAIL_ENABLED`, `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USE_TLS`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `ALERT_EMAIL_RECIPIENTS`

Admins can also adjust alert thresholds and toggle email notifications at runtime from the **Alert Settings** page, without restarting the app.

## API

Full REST API reference: [`docs/API.md`](docs/API.md).

## Deployment guides

- [Render](docs/DEPLOYMENT_RENDER.md)
- [Azure App Service](docs/DEPLOYMENT_AZURE.md)

## Tech stack

Python, Flask, Flask-SQLAlchemy, Flask-Login, Flask-WTF, Flask-Mail, psutil, APScheduler, SQLite, Bootstrap 5, Chart.js, Docker, GitHub Actions, pytest.
