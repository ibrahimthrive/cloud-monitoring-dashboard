"""SQLAlchemy ORM models."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app.extensions import db


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class MetricSnapshot(db.Model):
    __tablename__ = "metric_snapshots"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    cpu_percent = db.Column(db.Float, nullable=False)
    ram_percent = db.Column(db.Float, nullable=False)
    ram_used_mb = db.Column(db.Float, nullable=False)
    ram_total_mb = db.Column(db.Float, nullable=False)
    disk_percent = db.Column(db.Float, nullable=False)
    disk_used_gb = db.Column(db.Float, nullable=False)
    disk_total_gb = db.Column(db.Float, nullable=False)
    net_sent_kbps = db.Column(db.Float, nullable=False)
    net_recv_kbps = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "cpu_percent": self.cpu_percent,
            "ram_percent": self.ram_percent,
            "ram_used_mb": self.ram_used_mb,
            "ram_total_mb": self.ram_total_mb,
            "disk_percent": self.disk_percent,
            "disk_used_gb": self.disk_used_gb,
            "disk_total_gb": self.disk_total_gb,
            "net_sent_kbps": self.net_sent_kbps,
            "net_recv_kbps": self.net_recv_kbps,
        }


class AlertSettings(db.Model):
    """Singleton-style table holding the active alert thresholds."""

    __tablename__ = "alert_settings"

    id = db.Column(db.Integer, primary_key=True)
    cpu_threshold = db.Column(db.Float, nullable=False, default=85.0)
    ram_threshold = db.Column(db.Float, nullable=False, default=85.0)
    disk_threshold = db.Column(db.Float, nullable=False, default=90.0)
    email_enabled = db.Column(db.Boolean, default=False, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "cpu_threshold": self.cpu_threshold,
            "ram_threshold": self.ram_threshold,
            "disk_threshold": self.disk_threshold,
            "email_enabled": self.email_enabled,
        }


class AlertLog(db.Model):
    __tablename__ = "alert_logs"

    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    metric_type = db.Column(db.String(32), nullable=False)
    value = db.Column(db.Float, nullable=False)
    threshold = db.Column(db.Float, nullable=False)
    message = db.Column(db.String(255), nullable=False)
    email_sent = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "timestamp": self.timestamp.isoformat(),
            "metric_type": self.metric_type,
            "value": self.value,
            "threshold": self.threshold,
            "message": self.message,
            "email_sent": self.email_sent,
        }
