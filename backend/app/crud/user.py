from sqlalchemy.orm import Session
from app.models.user import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Retrieve a user by their ID."""
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Retrieve a user by their username."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    """Retrieve a user by their email address."""
    return db.query(User).filter(User.email == email).first()


def create_user(db: Session, username: str, email: str, password_hash: str) -> User:
    """Create a new user with the given credentials."""
    db_user = User(
        username=username,
        email=email,
        password_hash=password_hash
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user_id: int, **kwargs) -> User | None:
    """Update a user's attributes. Returns None if user not found."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return None

    for key, value in kwargs.items():
        if hasattr(db_user, key):
            setattr(db_user, key, value)

    db.commit()
    db.refresh(db_user)
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """Delete a user by their ID. Returns True if deleted, False if not found."""
    db_user = db.query(User).filter(User.id == user_id).first()
    if db_user is None:
        return False

    db.delete(db_user)
    db.commit()
    return True
