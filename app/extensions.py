"""Shared Flask extension instances (initialized in app/__init__.py)."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_wtf import CSRFProtect
from apscheduler.schedulers.background import BackgroundScheduler

db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()
csrf = CSRFProtect()
scheduler = BackgroundScheduler(daemon=True)

login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"
