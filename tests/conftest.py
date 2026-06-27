import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.monitoring.alerts import reset_cooldowns


@pytest.fixture()
def app():
    reset_cooldowns()
    application = create_app("testing")
    yield application
    with application.app_context():
        db.session.remove()
        db.drop_all()
    reset_cooldowns()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def admin_user(app):
    with app.app_context():
        user = User(username="admin", email="admin@example.com", is_admin=True)
        user.set_password("supersecret1")
        db.session.add(user)
        db.session.commit()
        return user.id


@pytest.fixture()
def login(client, admin_user):
    client.post("/auth/login", data={"username": "admin", "password": "supersecret1"}, follow_redirects=True)
    return client
