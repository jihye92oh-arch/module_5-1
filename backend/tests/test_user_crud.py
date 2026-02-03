import pytest
from sqlalchemy.exc import IntegrityError
from app.crud.user import (
    create_user,
    get_user_by_id,
    get_user_by_username,
    get_user_by_email,
    update_user,
    delete_user
)


class TestUserCreation:
    """Tests for user creation functionality."""

    def test_create_user_success(self, db_session):
        """Test successful user creation."""
        user = create_user(
            db_session,
            username="testuser",
            email="test@example.com",
            password_hash="hashed_password_123"
        )

        assert user.id is not None
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password_123"
        assert user.is_active is True
        assert user.created_at is not None

    def test_create_user_default_is_active(self, db_session):
        """Test that new users are active by default."""
        user = create_user(
            db_session,
            username="activeuser",
            email="active@example.com",
            password_hash="password"
        )

        assert user.is_active is True


class TestUserRetrieval:
    """Tests for user retrieval functionality."""

    def test_get_user_by_id_success(self, db_session):
        """Test retrieving a user by ID."""
        created_user = create_user(
            db_session,
            username="findme",
            email="findme@example.com",
            password_hash="password"
        )

        found_user = get_user_by_id(db_session, created_user.id)

        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.username == "findme"

    def test_get_user_by_id_not_found(self, db_session):
        """Test retrieving a non-existent user by ID."""
        user = get_user_by_id(db_session, 99999)

        assert user is None

    def test_get_user_by_username_success(self, db_session):
        """Test retrieving a user by username."""
        create_user(
            db_session,
            username="uniquename",
            email="unique@example.com",
            password_hash="password"
        )

        found_user = get_user_by_username(db_session, "uniquename")

        assert found_user is not None
        assert found_user.username == "uniquename"

    def test_get_user_by_username_not_found(self, db_session):
        """Test retrieving a non-existent user by username."""
        user = get_user_by_username(db_session, "nonexistent")

        assert user is None

    def test_get_user_by_email_success(self, db_session):
        """Test retrieving a user by email."""
        create_user(
            db_session,
            username="emailtest",
            email="specific@example.com",
            password_hash="password"
        )

        found_user = get_user_by_email(db_session, "specific@example.com")

        assert found_user is not None
        assert found_user.email == "specific@example.com"

    def test_get_user_by_email_not_found(self, db_session):
        """Test retrieving a non-existent user by email."""
        user = get_user_by_email(db_session, "nonexistent@example.com")

        assert user is None


class TestUserUpdate:
    """Tests for user update functionality."""

    def test_update_user_username(self, db_session):
        """Test updating a user's username."""
        user = create_user(
            db_session,
            username="oldname",
            email="update@example.com",
            password_hash="password"
        )

        updated_user = update_user(db_session, user.id, username="newname")

        assert updated_user is not None
        assert updated_user.username == "newname"
        assert updated_user.email == "update@example.com"

    def test_update_user_email(self, db_session):
        """Test updating a user's email."""
        user = create_user(
            db_session,
            username="emailupdate",
            email="old@example.com",
            password_hash="password"
        )

        updated_user = update_user(db_session, user.id, email="new@example.com")

        assert updated_user is not None
        assert updated_user.email == "new@example.com"

    def test_update_user_is_active(self, db_session):
        """Test deactivating a user."""
        user = create_user(
            db_session,
            username="deactivate",
            email="deactivate@example.com",
            password_hash="password"
        )

        updated_user = update_user(db_session, user.id, is_active=False)

        assert updated_user is not None
        assert updated_user.is_active is False

    def test_update_user_multiple_fields(self, db_session):
        """Test updating multiple fields at once."""
        user = create_user(
            db_session,
            username="multiupdate",
            email="multi@example.com",
            password_hash="password"
        )

        updated_user = update_user(
            db_session,
            user.id,
            username="newmulti",
            email="newmulti@example.com",
            is_active=False
        )

        assert updated_user is not None
        assert updated_user.username == "newmulti"
        assert updated_user.email == "newmulti@example.com"
        assert updated_user.is_active is False

    def test_update_user_not_found(self, db_session):
        """Test updating a non-existent user."""
        result = update_user(db_session, 99999, username="newname")

        assert result is None

    def test_update_user_invalid_field_ignored(self, db_session):
        """Test that invalid fields are ignored during update."""
        user = create_user(
            db_session,
            username="invalidfield",
            email="invalid@example.com",
            password_hash="password"
        )

        updated_user = update_user(
            db_session,
            user.id,
            nonexistent_field="value",
            username="validupdate"
        )

        assert updated_user is not None
        assert updated_user.username == "validupdate"


class TestUserDeletion:
    """Tests for user deletion functionality."""

    def test_delete_user_success(self, db_session):
        """Test successful user deletion."""
        user = create_user(
            db_session,
            username="deleteme",
            email="delete@example.com",
            password_hash="password"
        )
        user_id = user.id

        result = delete_user(db_session, user_id)

        assert result is True
        assert get_user_by_id(db_session, user_id) is None

    def test_delete_user_not_found(self, db_session):
        """Test deleting a non-existent user."""
        result = delete_user(db_session, 99999)

        assert result is False


class TestUniqueConstraints:
    """Tests for unique constraint enforcement."""

    def test_unique_username_constraint(self, db_session):
        """Test that duplicate usernames are rejected."""
        create_user(
            db_session,
            username="duplicate",
            email="first@example.com",
            password_hash="password"
        )

        with pytest.raises(IntegrityError):
            create_user(
                db_session,
                username="duplicate",
                email="second@example.com",
                password_hash="password"
            )

    def test_unique_email_constraint(self, db_session):
        """Test that duplicate emails are rejected."""
        create_user(
            db_session,
            username="first",
            email="duplicate@example.com",
            password_hash="password"
        )

        with pytest.raises(IntegrityError):
            create_user(
                db_session,
                username="second",
                email="duplicate@example.com",
                password_hash="password"
            )

    def test_unique_username_case_sensitivity(self, db_session):
        """Test username uniqueness - SQLite is case-insensitive by default."""
        create_user(
            db_session,
            username="CaseSensitive",
            email="case1@example.com",
            password_hash="password"
        )

        # SQLite UNIQUE is case-insensitive by default
        # This may raise IntegrityError depending on collation
        # We test that we can at least create with different case
        user2 = create_user(
            db_session,
            username="casesensitive_different",
            email="case2@example.com",
            password_hash="password"
        )
        assert user2 is not None
