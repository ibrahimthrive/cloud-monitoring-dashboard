from flask import render_template, redirect, url_for
from flask_login import login_required, current_user

from app.dashboard import dashboard_bp


@dashboard_bp.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))
    return redirect(url_for("auth.login"))


@dashboard_bp.route("/dashboard")
@login_required
def index():
    return render_template("dashboard.html")


@dashboard_bp.route("/processes")
@login_required
def processes():
    return render_template("processes.html")


@dashboard_bp.route("/services")
@login_required
def services():
    return render_template("services.html")


@dashboard_bp.route("/settings")
@login_required
def settings():
    return render_template("settings.html")
