# Deploying to Render

Render builds the existing `Dockerfile`, so no extra build configuration is required.

## 1. Push the repo to GitHub

Render deploys from a Git repository (GitHub, GitLab, or a public Git URL).

## 2. Create a new Web Service

1. In the Render dashboard, click **New > Web Service**.
2. Connect the GitHub repository containing this project.
3. Render detects the `Dockerfile` automatically — choose **Docker** as the environment if prompted.
4. Set the **Instance Type** (the free tier is sufficient for testing; metrics collection is lightweight).

## 3. Configure environment variables

Under **Environment**, add the variables from `.env.example`. At minimum:

| Key | Value |
| --- | --- |
| `SECRET_KEY` | a random 32+ character string |
| `FLASK_ENV` | `production` |
| `DATABASE_URL` | `sqlite:////app/instance/monitoring.db` |
| `METRICS_COLLECTION_INTERVAL_SECONDS` | `15` |
| `LIVE_REFRESH_INTERVAL_SECONDS` | `5` |
| `MAIL_ENABLED` | `true` if you want email alerts |
| `MAIL_SERVER`, `MAIL_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `ALERT_EMAIL_RECIPIENTS` | your SMTP provider's credentials |

Render injects `PORT` automatically — the app already reads `PORT` from the environment, and the Dockerfile's gunicorn `CMD` binds to `0.0.0.0:5000`. If Render assigns a different port, override the start command in the Render dashboard to:
```
gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 run:app
```

## 4. Persistent storage: use Render Postgres

SQLite data written to the container's filesystem is **not persisted** across deploys or restarts on Render — registered users (including the admin account) disappear and logins start failing with "Invalid username or password" the moment the container recycles. This project now ships `psycopg2-binary` so it can talk to Postgres instead:

1. In the Render dashboard, click **New > PostgreSQL** and create a free database.
2. Once it's provisioned, copy the **Internal Database URL** (starts with `postgres://`).
3. On the web service's **Environment** tab, set `DATABASE_URL` to that value. `app/config.py` automatically rewrites the `postgres://` scheme to `postgresql://` for SQLAlchemy.
4. Redeploy. `db.create_all()` runs against Postgres on startup and creates the tables there; register the first account again to get a fresh admin.

(A paid **Render Disk** mounted at `/app/instance` is an alternative if you want to keep SQLite, but Postgres is free and survives restarts without extra disk cost.)

## 5. Deploy

Click **Create Web Service**. Render builds the Docker image and starts the container. Visit the assigned `*.onrender.com` URL, register the first account (it is automatically granted admin rights), and confirm metrics populate within a few seconds.

## 6. Health checks

Render pings the service root by default. The Dockerfile already defines a `HEALTHCHECK` hitting `/auth/login`; you can also point Render's health check path explicitly to `/auth/login` in the service settings.
