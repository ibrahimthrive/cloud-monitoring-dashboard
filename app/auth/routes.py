import logging

from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from app.auth import auth_bp
from app.auth.forms import LoginForm, RegistrationForm
from app.extensions import db
from app.models import User

logger = logging.getLogger(__name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            logger.info("User logged in: %s", user.username)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("dashboard.index"))
        flash("Invalid username or password.", "danger")

    return render_template("login.html", form=form)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    form = RegistrationForm()
    if form.validate_on_submit():
        is_first_user = User.query.count() == 0
        user = User(username=form.username.data, email=form.email.data, is_admin=is_first_user)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        logger.info("New user registered: %s", user.username)
        flash("Account created successfully. Please sign in.", "success")
        return redirect(url_for("auth.login"))

    return render_template("register.html", form=form)


@auth_bp.route("/logout")
@login_required
def logout():
    logger.info("User logged out: %s", current_user.username)
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
