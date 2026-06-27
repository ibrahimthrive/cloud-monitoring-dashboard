"""Application factory."""
import os

from flask import Flask, render_template

from app.config import get_config
from app.extensions import db, login_manager, mail, csrf, scheduler
from app.logging_config import configure_logging


def create_app(config_name=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(get_config(config_name))

    os.makedirs(app.instance_path, exist_ok=True)

    configure_logging(app)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    from app.auth import auth_bp
    from app.dashboard import dashboard_bp
    from app.api import api_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(api_bp)

    @app.errorhandler(404)
    def not_found(_error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(_error):
        return render_template("500.html"), 500

    with app.app_context():
        db.create_all()

    if app.config.get("SCHEDULER_ENABLED", True) and not app.config.get("TESTING"):
        from app.monitoring.collector import init_scheduler

        init_scheduler(app, scheduler)

    return app
