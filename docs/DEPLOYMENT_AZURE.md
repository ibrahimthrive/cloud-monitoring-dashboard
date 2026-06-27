# Deploying to Azure (App Service for Containers)

This guide uses Azure App Service's container support, deploying the image from Azure Container Registry (ACR).

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- Docker installed locally

## 1. Create a resource group

```bash
az group create --name cloud-monitor-rg --location eastus
```

## 2. Create an Azure Container Registry and push the image

```bash
az acr create --resource-group cloud-monitor-rg --name cloudmonitoracr --sku Basic
az acr login --name cloudmonitoracr

docker build -t cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest .
docker push cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest
```

## 3. Create an App Service plan and Web App

```bash
az appservice plan create \
  --name cloud-monitor-plan \
  --resource-group cloud-monitor-rg \
  --is-linux \
  --sku B1

az webapp create \
  --resource-group cloud-monitor-rg \
  --plan cloud-monitor-plan \
  --name cloud-monitor-dashboard \
  --deployment-container-image-name cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest
```

## 4. Grant the Web App access to ACR

```bash
az webapp config container set \
  --name cloud-monitor-dashboard \
  --resource-group cloud-monitor-rg \
  --container-image-name cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest \
  --container-registry-url https://cloudmonitoracr.azurecr.io

az webapp identity assign --name cloud-monitor-dashboard --resource-group cloud-monitor-rg
az acr update --name cloudmonitoracr --admin-enabled true
```

(Using `--admin-enabled true` is the quickest path; for production, prefer a managed identity with an ACR `AcrPull` role assignment instead of admin credentials.)

## 5. Configure environment variables (App Settings)

```bash
az webapp config appsettings set \
  --resource-group cloud-monitor-rg \
  --name cloud-monitor-dashboard \
  --settings \
    SECRET_KEY="<random-32-char-string>" \
    FLASK_ENV="production" \
    DATABASE_URL="sqlite:////app/instance/monitoring.db" \
    METRICS_COLLECTION_INTERVAL_SECONDS="15" \
    LIVE_REFRESH_INTERVAL_SECONDS="5" \
    MAIL_ENABLED="true" \
    MAIL_SERVER="smtp.sendgrid.net" \
    MAIL_PORT="587" \
    MAIL_USERNAME="apikey" \
    MAIL_PASSWORD="<sendgrid-api-key>" \
    ALERT_EMAIL_RECIPIENTS="ops@example.com" \
    WEBSITES_PORT="5000"
```

`WEBSITES_PORT` tells App Service which port the container listens on (the Dockerfile exposes `5000`).

## 6. Persistent storage for SQLite

App Service for Containers uses an ephemeral filesystem by default — data in `/app/instance` is lost on restart or scale events. To persist it:

- Enable **Persistent storage** for containers: set `WEBSITES_ENABLE_APP_SERVICE_STORAGE=true` and the `/home` path persists, so configure `DATABASE_URL=sqlite:////home/instance/monitoring.db` and mount accordingly, or
- For production workloads, switch to **Azure Database for PostgreSQL** and update `DATABASE_URL` (e.g. `postgresql+psycopg2://user:pass@host/dbname`) plus add `psycopg2-binary` to `requirements.txt`.

## 7. Deploy updates

```bash
docker build -t cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest .
docker push cloudmonitoracr.azurecr.io/cloud-monitoring-dashboard:latest
az webapp restart --name cloud-monitor-dashboard --resource-group cloud-monitor-rg
```

## 8. Verify

```bash
az webapp browse --name cloud-monitor-dashboard --resource-group cloud-monitor-rg
```

Register the first account (granted admin automatically) and confirm the dashboard populates live metrics.
