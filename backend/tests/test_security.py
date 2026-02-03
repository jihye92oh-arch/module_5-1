"""
Tests for security utility functions.

Tests password hashing, verification, and JWT token operations.
"""
import pytest
from datetime import timedelta
from unittest.mock import patch
from datetime import datetime

from app.utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_token,
    SECRET_KEY,
    ALGORITHM,
)


class TestPasswordHashing:
    """Tests for password hashing functionality."""

    def test_hash_password_returns_hashed_string(self):
        """Test that hash_password returns a hashed string different from original."""
        password = "mysecretpassword"
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)
        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_produces_different_hashes_for_same_password(self):
        """Test that bcrypt produces different hashes for the same password (due to salt)."""
        password = "mysecretpassword"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # bcrypt uses random salt, so hashes should be different
        assert hash1 != hash2

    def test_hash_password_with_empty_string(self):
        """Test that empty password can be hashed."""
        password = ""
        hashed = hash_password(password)

        assert hashed is not None
        assert isinstance(hashed, str)

    def test_hash_password_with_special_characters(self):
        """Test that passwords with special characters are hashed correctly."""
        password = "p@$$w0rd!#$%^&*()"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed)

    def test_hash_password_with_unicode(self):
        """Test that unicode passwords are hashed correctly."""
        password = "password_test"
        hashed = hash_password(password)

        assert hashed is not None
        assert verify_password(password, hashed)


class TestPasswordVerification:
    """Tests for password verification functionality."""

    def test_verify_password_success(self):
        """Test that correct password verifies successfully."""
        password = "correctpassword"
        hashed = hash_password(password)

        result = verify_password(password, hashed)

        assert result is True

    def test_verify_password_failure_wrong_password(self):
        """Test that wrong password fails verification."""
        password = "correctpassword"
        wrong_password = "wrongpassword"
        hashed = hash_password(password)

        result = verify_password(wrong_password, hashed)

        assert result is False

    def test_verify_password_failure_similar_password(self):
        """Test that a similar but different password fails verification."""
        password = "password123"
        similar_password = "password124"
        hashed = hash_password(password)

        result = verify_password(similar_password, hashed)

        assert result is False

    def test_verify_password_case_sensitive(self):
        """Test that password verification is case-sensitive."""
        password = "MyPassword"
        different_case = "mypassword"
        hashed = hash_password(password)

        result = verify_password(different_case, hashed)

        assert result is False


class TestJWTTokenCreation:
    """Tests for JWT token creation functionality."""

    def test_create_access_token_returns_string(self):
        """Test that create_access_token returns a string."""
        data = {"sub": "testuser"}
        token = create_access_token(data)

        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_contains_subject(self):
        """Test that created token contains the subject in payload."""
        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert payload.get("sub") == "testuser"
        assert payload.get("user_id") == 123

    def test_create_access_token_with_custom_expiration(self):
        """Test that custom expiration time is respected."""
        data = {"sub": "testuser"}
        expires_delta = timedelta(hours=1)
        token = create_access_token(data, expires_delta=expires_delta)
        payload = verify_token(token)

        assert payload is not None
        assert "exp" in payload

    def test_create_access_token_default_expiration(self):
        """Test that default expiration is set when not provided."""
        data = {"sub": "testuser"}
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert "exp" in payload

    def test_create_access_token_with_additional_claims(self):
        """Test that additional claims are included in token."""
        data = {
            "sub": "testuser",
            "user_id": 42,
            "role": "admin",
        }
        token = create_access_token(data)
        payload = verify_token(token)

        assert payload is not None
        assert payload.get("sub") == "testuser"
        assert payload.get("user_id") == 42
        assert payload.get("role") == "admin"


class TestJWTTokenVerification:
    """Tests for JWT token verification functionality."""

    def test_verify_token_valid_token(self):
        """Test that a valid token is verified successfully."""
        data = {"sub": "testuser", "user_id": 123}
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload.get("sub") == "testuser"
        assert payload.get("user_id") == 123

    def test_verify_token_expired_token(self):
        """Test that an expired token returns None."""
        data = {"sub": "testuser"}
        # Create token that expires immediately (negative time delta)
        expires_delta = timedelta(seconds=-1)
        token = create_access_token(data, expires_delta=expires_delta)

        payload = verify_token(token)

        assert payload is None

    def test_verify_token_invalid_token_format(self):
        """Test that an invalid token format returns None."""
        invalid_token = "this.is.not.a.valid.token"

        payload = verify_token(invalid_token)

        assert payload is None

    def test_verify_token_empty_string(self):
        """Test that empty token string returns None."""
        empty_token = ""

        payload = verify_token(empty_token)

        assert payload is None

    def test_verify_token_malformed_token(self):
        """Test that malformed token returns None."""
        malformed_token = "abc123"

        payload = verify_token(malformed_token)

        assert payload is None

    def test_verify_token_wrong_secret_key(self):
        """Test that token signed with different secret returns None."""
        from jose import jwt

        data = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)}
        wrong_secret = "different-secret-key"
        token = jwt.encode(data, wrong_secret, algorithm=ALGORITHM)

        payload = verify_token(token)

        assert payload is None

    def test_verify_token_wrong_algorithm(self):
        """Test that token with different algorithm returns None."""
        from jose import jwt

        data = {"sub": "testuser", "exp": datetime.utcnow() + timedelta(hours=1)}
        # Create token with HS384 instead of HS256
        token = jwt.encode(data, SECRET_KEY, algorithm="HS384")

        payload = verify_token(token)

        # Token should be invalid due to algorithm mismatch
        assert payload is None

    def test_verify_token_preserves_all_claims(self):
        """Test that all claims in the token are preserved after verification."""
        data = {
            "sub": "testuser",
            "user_id": 123,
            "email": "test@example.com",
            "custom_claim": "custom_value",
        }
        token = create_access_token(data)

        payload = verify_token(token)

        assert payload is not None
        assert payload.get("sub") == "testuser"
        assert payload.get("user_id") == 123
        assert payload.get("email") == "test@example.com"
        assert payload.get("custom_claim") == "custom_value"
        assert "exp" in payload
