def test_register_creates_user(client):
    response = client.post(
        "/auth/register",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Account created successfully" in response.data


def test_register_rejects_duplicate_username(client, admin_user):
    response = client.post(
        "/auth/register",
        data={
            "username": "admin",
            "email": "another@example.com",
            "password": "password123",
            "confirm_password": "password123",
        },
    )
    assert b"Username already taken" in response.data


def test_login_success(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "supersecret1"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Dashboard" in response.data or b"dashboard" in response.data


def test_login_invalid_password(client, admin_user):
    response = client.post(
        "/auth/login",
        data={"username": "admin", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=True)
    assert b"Sign In" in response.data or b"sign in" in response.data.lower()


def test_logout(login):
    response = login.get("/auth/logout", follow_redirects=True)
    assert b"logged out" in response.data.lower()
