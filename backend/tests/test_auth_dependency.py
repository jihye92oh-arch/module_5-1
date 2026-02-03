"""
Tests for authentication dependency functions.

Tests the get_current_user dependency in isolation.
"""
import pytest
from datetime import timedelta
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base
from app.dependencies.auth import get_current_user
from app.models import User
from app.utils.security import hash_password, create_access_token


# Test database setup
TEST_DATABASE_URL = "sqlite:///:memory:"
test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture
def db_session():
    """Create a fresh database session for each test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def test_user(db_session):
    """Create a test user in the database."""
    user = User(
        username="depuser",
        email="dep@example.com",
        password_hash=hash_password("testpass123"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def inactive_user(db_session):
    """Create an inactive test user in the database."""
    user = User(
        username="inactiveuser",
        email="inactive@example.com",
        password_hash=hash_password("testpass123"),
        is_active=False,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def valid_token(test_user):
    """Create a valid token for the test user."""
    return create_access_token(
        data={"sub": test_user.username, "user_id": test_user.id}
    )


class TestGetCurrentUserWithValidToken:
    """Tests for get_current_user with valid tokens."""

    def test_get_current_user_valid_token(self, db_session, test_user, valid_token):
        """Test that get_current_user returns the correct user with valid token."""
        result = get_current_user(token=valid_token, db=db_session)

        assert result is not None
        assert result.id == test_user.id
        assert result.username == test_user.username
        assert result.email == test_user.email

    def test_get_current_user_returns_user_object(self, db_session, test_user, valid_token):
        """Test that get_current_user returns a User instance."""
        result = get_current_user(token=valid_token, db=db_session)

        assert isinstance(result, User)

    def test_get_current_user_with_user_id_only(self, db_session, test_user):
        """Test get_current_user when token has user_id but verifies correctly."""
        token = create_access_token(
            data={"sub": test_user.username, "user_id": test_user.id}
        )

        result = get_current_user(token=token, db=db_session)

        assert result.id == test_user.id

    def test_get_current_user_with_username_only(self, db_session, test_user):
        """Test get_current_user when token has username but no user_id."""
        token = create_access_token(
            data={"sub": test_user.username}  # No user_id
        )

        result = get_current_user(token=token, db=db_session)

        assert result.username == test_user.username


class TestGetCurrentUserWithNoToken:
    """Tests for get_current_user when no token is provided."""

    def test_get_current_user_empty_token(self, db_session):
        """Test that empty token raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="", db=db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail


class TestGetCurrentUserWithInvalidToken:
    """Tests for get_current_user with invalid tokens."""

    def test_get_current_user_invalid_token_format(self, db_session):
        """Test that invalid token format raises HTTPException."""
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token="invalid_token_string", db=db_session)

        assert exc_info.value.status_code == 401
        assert "Could not validate credentials" in exc_info.value.detail

    def test_get_current_user_malformed_jwt(self, db_session):
        """Test that malformed JWT raises HTTPException."""
        malformed_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.malformed"

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=malformed_token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_expired_token(self, db_session, test_user):
        """Test that expired token raises HTTPException."""
        expired_token = create_access_token(
            data={"sub": test_user.username, "user_id": test_user.id},
            expires_delta=timedelta(seconds=-1),  # Already expired
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=expired_token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_token_without_sub(self, db_session):
        """Test that token without 'sub' claim raises HTTPException."""
        token = create_access_token(
            data={"user_id": 123}  # No 'sub' claim
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_token_with_wrong_secret(self, db_session):
        """Test that token signed with wrong secret raises HTTPException."""
        from jose import jwt

        wrong_secret = "wrong-secret-key"
        data = {
            "sub": "testuser",
            "user_id": 1,
            "exp": timedelta(hours=1).total_seconds(),
        }
        token = jwt.encode(data, wrong_secret, algorithm="HS256")

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401


class TestGetCurrentUserWithNonExistentUser:
    """Tests for get_current_user when user doesn't exist in database."""

    def test_get_current_user_nonexistent_user_id(self, db_session):
        """Test that token for non-existent user_id raises HTTPException."""
        token = create_access_token(
            data={"sub": "ghostuser", "user_id": 99999}
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_nonexistent_username(self, db_session):
        """Test that token for non-existent username raises HTTPException."""
        token = create_access_token(
            data={"sub": "nonexistentuser"}  # No user_id, only username
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_deleted_user(self, db_session, test_user, valid_token):
        """Test that token for deleted user raises HTTPException."""
        # Delete the user
        db_session.delete(test_user)
        db_session.commit()

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=valid_token, db=db_session)

        assert exc_info.value.status_code == 401


class TestGetCurrentUserWithInactiveUser:
    """Tests for get_current_user when user is inactive."""

    def test_get_current_user_inactive_user(self, db_session, inactive_user):
        """Test that token for inactive user raises HTTPException."""
        token = create_access_token(
            data={"sub": inactive_user.username, "user_id": inactive_user.id}
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401
        assert "User account is inactive" in exc_info.value.detail

    def test_get_current_user_user_deactivated_after_token_creation(
        self, db_session, test_user, valid_token
    ):
        """Test that deactivating a user invalidates their existing token."""
        # Verify token works first
        result = get_current_user(token=valid_token, db=db_session)
        assert result is not None

        # Deactivate the user
        test_user.is_active = False
        db_session.commit()

        # Token should now be invalid
        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=valid_token, db=db_session)

        assert exc_info.value.status_code == 401
        assert "User account is inactive" in exc_info.value.detail


class TestGetCurrentUserEdgeCases:
    """Edge case tests for get_current_user."""

    def test_get_current_user_with_extra_claims(self, db_session, test_user):
        """Test that extra claims in token don't affect user retrieval."""
        token = create_access_token(
            data={
                "sub": test_user.username,
                "user_id": test_user.id,
                "extra_claim": "extra_value",
                "another_claim": 12345,
            }
        )

        result = get_current_user(token=token, db=db_session)

        assert result.id == test_user.id

    def test_get_current_user_token_sub_is_none(self, db_session):
        """Test that token with None as sub raises HTTPException."""
        token = create_access_token(
            data={"sub": None, "user_id": 1}
        )

        with pytest.raises(HTTPException) as exc_info:
            get_current_user(token=token, db=db_session)

        assert exc_info.value.status_code == 401

    def test_get_current_user_multiple_calls_same_token(self, db_session, test_user, valid_token):
        """Test that same token can be used multiple times."""
        result1 = get_current_user(token=valid_token, db=db_session)
        result2 = get_current_user(token=valid_token, db=db_session)

        assert result1.id == result2.id == test_user.id

    def test_get_current_user_different_users_different_tokens(self, db_session, test_user):
        """Test that different users get correctly identified by their tokens."""
        # Create another user
        user2 = User(
            username="anotheruser",
            email="another@example.com",
            password_hash=hash_password("pass123"),
            is_active=True,
        )
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)

        token1 = create_access_token(data={"sub": test_user.username, "user_id": test_user.id})
        token2 = create_access_token(data={"sub": user2.username, "user_id": user2.id})

        result1 = get_current_user(token=token1, db=db_session)
        result2 = get_current_user(token=token2, db=db_session)

        assert result1.id == test_user.id
        assert result2.id == user2.id
        assert result1.id != result2.id
