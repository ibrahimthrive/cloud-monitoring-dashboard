"""Application configuration loaded from environment variables."""
import os
from datetime import timedelta

basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _bool(value, default=False):
    if value is None:
        return default
    return str(value).strip().lower() in ("1", "true", "yes", "on")


def _normalize_db_uri(uri):
    # Render (and Heroku) hand out "postgres://" connection strings, but
    # SQLAlchemy 1.4+ only recognizes the "postgresql://" scheme.
    if uri.startswith("postgres://"):
        return "postgresql://" + uri[len("postgres://"):]
    return uri


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-change-me")

    SQLALCHEMY_DATABASE_URI = _normalize_db_uri(os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'instance', 'monitoring.db')}"
    ))
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    PERMANENT_SESSION_LIFETIME = timedelta(hours=int(os.environ.get("SESSION_LIFETIME_HOURS", 12)))

    # Metrics collection
    METRICS_COLLECTION_INTERVAL_SECONDS = int(os.environ.get("METRICS_COLLECTION_INTERVAL_SECONDS", 15))
    METRICS_RETENTION_DAYS = int(os.environ.get("METRICS_RETENTION_DAYS", 7))
    LIVE_REFRESH_INTERVAL_SECONDS = int(os.environ.get("LIVE_REFRESH_INTERVAL_SECONDS", 5))

    # Alert thresholds (defaults, can be overridden per-deployment in Settings table)
    DEFAULT_CPU_ALERT_THRESHOLD = float(os.environ.get("DEFAULT_CPU_ALERT_THRESHOLD", 85.0))
    DEFAULT_RAM_ALERT_THRESHOLD = float(os.environ.get("DEFAULT_RAM_ALERT_THRESHOLD", 85.0))
    DEFAULT_DISK_ALERT_THRESHOLD = float(os.environ.get("DEFAULT_DISK_ALERT_THRESHOLD", 90.0))
    ALERT_COOLDOWN_SECONDS = int(os.environ.get("ALERT_COOLDOWN_SECONDS", 300))

    # Mail / email notifications
    MAIL_ENABLED = _bool(os.environ.get("MAIL_ENABLED"), False)
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = _bool(os.environ.get("MAIL_USE_TLS"), True)
    MAIL_USE_SSL = _bool(os.environ.get("MAIL_USE_SSL"), False)
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.environ.get("MAIL_DEFAULT_SENDER", MAIL_USERNAME)
    ALERT_EMAIL_RECIPIENTS = [
        addr.strip() for addr in os.environ.get("ALERT_EMAIL_RECIPIENTS", "").split(",") if addr.strip()
    ]

    LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO")
    LOG_FILE = os.environ.get("LOG_FILE", os.path.join(basedir, "logs", "app.log"))

    WTF_CSRF_ENABLED = True


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SCHEDULER_ENABLED = False


class ProductionConfig(Config):
    DEBUG = False


config_by_name = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}


def get_config(name=None):
    name = name or os.environ.get("FLASK_ENV", "development")
    return config_by_name.get(name, DevelopmentConfig)
