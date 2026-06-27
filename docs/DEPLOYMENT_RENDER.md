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

## 4. Persistent storage for SQLite

SQLite data written to the container's filesystem is **not persisted** across deploys on Render's free tier. For real persistence:

- Add a **Render Disk** (paid plans) mounted at `/app/instance`, or
- Point `DATABASE_URL` at a managed Postgres instance (Render offers free Postgres) and switch the SQLAlchemy driver to `psycopg2-binary` — the ORM layer in `app/models.py` requires no changes, only the connection string and an added dependency.

## 5. Deploy

Click **Create Web Service**. Render builds the Docker image and starts the container. Visit the assigned `*.onrender.com` URL, register the first account (it is automatically granted admin rights), and confirm metrics populate within a few seconds.

## 6. Health checks

Render pings the service root by default. The Dockerfile already defines a `HEALTHCHECK` hitting `/auth/login`; you can also point Render's health check path explicitly to `/auth/login` in the service settings.
