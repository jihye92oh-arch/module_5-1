"""
Tests for authentication API endpoints.

Tests registration, login, and current user endpoints.
"""
import pytest
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.utils.security import hash_password, create_access_token


# Test database setup - create a single engine for all tests
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh database for each test."""
    # Import all models to ensure they are registered with Base
    from app.models import User  # noqa: F401

    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    yield {"engine": engine, "SessionLocal": TestingSessionLocal}

    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client(test_db):
    """Create a test client with fresh database."""
    from app.main import app

    def override_get_db():
        db = test_db["SessionLocal"]()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield TestClient(app)

    # Clean up the override
    app.dependency_overrides.clear()


@pytest.fixture
def test_user_data():
    """Standard test user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123",
    }


@pytest.fixture
def registered_user(client, test_user_data):
    """Create a registered user and return the user data with ID."""
    response = client.post("/api/auth/register", json=test_user_data)
    assert response.status_code == 201
    return {**test_user_data, "id": response.json()["id"]}


@pytest.fixture
def auth_token(registered_user, client):
    """Get an auth token for the registered user."""
    response = client.post(
        "/api/auth/login",
        data={
            "username": registered_user["username"],
            "password": registered_user["password"],
        },
    )
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def db_session(test_db):
    """Get a database session for direct DB manipulation in tests."""
    session = test_db["SessionLocal"]()
    yield session
    session.close()


class TestRegistration:
    """Tests for POST /api/auth/register endpoint."""

    def test_register_success(self, client, test_user_data):
        """Test successful user registration."""
        response = client.post("/api/auth/register", json=test_user_data)

        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_register_duplicate_username(self, client, registered_user, test_user_data):
        """Test registration with duplicate username returns 400."""
        new_user_data = {
            "username": registered_user["username"],  # Same username
            "email": "different@example.com",
            "password": "password123",
        }

        response = client.post("/api/auth/register", json=new_user_data)

        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]

    def test_register_duplicate_email(self, client, registered_user, test_user_data):
        """Test registration with duplicate email returns 400."""
        new_user_data = {
            "username": "differentuser",
            "email": registered_user["email"],  # Same email
            "password": "password123",
        }

        response = client.post("/api/auth/register", json=new_user_data)

        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_short_username(self, client):
        """Test registration with short username returns validation error."""
        user_data = {
            "username": "ab",  # Less than 3 characters
            "email": "test@example.com",
            "password": "password123",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422
        # Pydantic validation error

    def test_register_short_password(self, client):
        """Test registration with short password returns validation error."""
        user_data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "12345",  # Less than 6 characters
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_invalid_email(self, client):
        """Test registration with invalid email returns validation error."""
        user_data = {
            "username": "testuser",
            "email": "not-an-email",
            "password": "password123",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422

    def test_register_missing_fields(self, client):
        """Test registration with missing fields returns validation error."""
        response = client.post("/api/auth/register", json={})

        assert response.status_code == 422

    def test_register_empty_username(self, client):
        """Test registration with empty username returns validation error."""
        user_data = {
            "username": "",
            "email": "test@example.com",
            "password": "password123",
        }

        response = client.post("/api/auth/register", json=user_data)

        assert response.status_code == 422


class TestLogin:
    """Tests for POST /api/auth/login endpoint."""

    def test_login_success_with_username(self, client, registered_user):
        """Test successful login using username."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_success_with_email(self, client, registered_user):
        """Test successful login using email address."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["email"],  # Email in username field
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_wrong_username(self, client, registered_user):
        """Test login with non-existent username returns 401."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": "nonexistentuser",
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_wrong_password(self, client, registered_user):
        """Test login with wrong password returns 401."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": "wrongpassword",
            },
        )

        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]

    def test_login_inactive_account(self, client, registered_user, db_session):
        """Test login with inactive account returns 401."""
        # Deactivate the user
        from app.models import User

        user = db_session.query(User).filter(User.username == registered_user["username"]).first()
        user.is_active = False
        db_session.commit()

        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )

        assert response.status_code == 401
        assert "User account is inactive" in response.json()["detail"]

    def test_login_jwt_token_valid(self, client, registered_user):
        """Test that JWT token returned from login is valid."""
        from app.utils.security import verify_token

        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )

        token = response.json()["access_token"]
        payload = verify_token(token)

        assert payload is not None
        assert payload.get("sub") == registered_user["username"]
        assert "user_id" in payload
        assert "exp" in payload

    def test_login_case_sensitive_password(self, client, registered_user):
        """Test that password is case-sensitive."""
        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"].upper(),  # Wrong case
            },
        )

        assert response.status_code == 401


class TestCurrentUser:
    """Tests for GET /api/auth/me endpoint."""

    def test_get_current_user_success(self, client, registered_user, auth_token):
        """Test getting authenticated user information."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["username"] == registered_user["username"]
        assert data["email"] == registered_user["email"]
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_current_user_no_token(self, client):
        """Test accessing /me without token returns 401."""
        response = client.get("/api/auth/me")

        assert response.status_code == 401

    def test_get_current_user_invalid_token(self, client):
        """Test accessing /me with invalid token returns 401."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401
        assert "Could not validate credentials" in response.json()["detail"]

    def test_get_current_user_expired_token(self, client, registered_user):
        """Test accessing /me with expired token returns 401."""
        # Create an expired token
        expired_token = create_access_token(
            data={"sub": registered_user["username"], "user_id": registered_user["id"]},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401

    def test_get_current_user_malformed_authorization_header(self, client):
        """Test accessing /me with malformed authorization header."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "InvalidFormat token123"},
        )

        assert response.status_code == 401

    def test_get_current_user_empty_bearer_token(self, client):
        """Test accessing /me with empty bearer token."""
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer "},
        )

        assert response.status_code == 401

    def test_get_current_user_token_for_nonexistent_user(self, client, registered_user, db_session):
        """Test accessing /me with token for deleted user returns 401."""
        # Get a valid token first
        response = client.post(
            "/api/auth/login",
            data={
                "username": registered_user["username"],
                "password": registered_user["password"],
            },
        )
        token = response.json()["access_token"]

        # Delete the user from database
        from app.models import User

        user = db_session.query(User).filter(User.username == registered_user["username"]).first()
        db_session.delete(user)
        db_session.commit()

        # Try to use the token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 401

    def test_get_current_user_inactive_user_token(self, client, registered_user, auth_token, db_session):
        """Test accessing /me after user becomes inactive returns 401."""
        # Deactivate the user
        from app.models import User

        user = db_session.query(User).filter(User.username == registered_user["username"]).first()
        user.is_active = False
        db_session.commit()

        # Try to use the existing token
        response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        assert response.status_code == 401
        assert "User account is inactive" in response.json()["detail"]


class TestAuthFlow:
    """Integration tests for complete authentication flow."""

    def test_full_auth_flow(self, client):
        """Test complete registration -> login -> access protected resource flow."""
        user_data = {
            "username": "flowuser",
            "email": "flow@example.com",
            "password": "flowpass123",
        }

        # Step 1: Register
        register_response = client.post("/api/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["id"]

        # Step 2: Login
        login_response = client.post(
            "/api/auth/login",
            data={"username": user_data["username"], "password": user_data["password"]},
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 3: Access protected resource
        me_response = client.get(
            "/api/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        assert me_response.json()["id"] == user_id
        assert me_response.json()["username"] == user_data["username"]

    def test_register_multiple_users(self, client):
        """Test that multiple unique users can be registered."""
        users = [
            {"username": "user1", "email": "user1@example.com", "password": "pass123"},
            {"username": "user2", "email": "user2@example.com", "password": "pass123"},
            {"username": "user3", "email": "user3@example.com", "password": "pass123"},
        ]

        for user_data in users:
            response = client.post("/api/auth/register", json=user_data)
            assert response.status_code == 201

    def test_different_users_get_different_tokens(self, client):
        """Test that different users receive different tokens."""
        users = [
            {"username": "tokenuser1", "email": "token1@example.com", "password": "pass123"},
            {"username": "tokenuser2", "email": "token2@example.com", "password": "pass123"},
        ]

        tokens = []
        for user_data in users:
            client.post("/api/auth/register", json=user_data)
            response = client.post(
                "/api/auth/login",
                data={"username": user_data["username"], "password": user_data["password"]},
            )
            tokens.append(response.json()["access_token"])

        # Tokens should be different
        assert tokens[0] != tokens[1]

    def test_token_identifies_correct_user(self, client):
        """Test that each token correctly identifies its associated user."""
        users = [
            {"username": "identify1", "email": "id1@example.com", "password": "pass123"},
            {"username": "identify2", "email": "id2@example.com", "password": "pass123"},
        ]

        for user_data in users:
            # Register
            client.post("/api/auth/register", json=user_data)

            # Login
            login_response = client.post(
                "/api/auth/login",
                data={"username": user_data["username"], "password": user_data["password"]},
            )
            token = login_response.json()["access_token"]

            # Verify identity
            me_response = client.get(
                "/api/auth/me",
                headers={"Authorization": f"Bearer {token}"},
            )
            assert me_response.json()["username"] == user_data["username"]
            assert me_response.json()["email"] == user_data["email"]
