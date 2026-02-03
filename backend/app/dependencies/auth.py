from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.crud import user as user_crud
from app.utils.security import verify_token


# OAuth2 scheme for token extraction from Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: The JWT token from the Authorization header.
        db: Database session.

    Returns:
        The authenticated User object.

    Raises:
        HTTPException: 401 if token is invalid or user not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Verify the token
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception

    # Extract user info from token
    username: str = payload.get("sub")
    user_id: int = payload.get("user_id")

    if username is None:
        raise credentials_exception

    # Get user from database
    if user_id:
        user = user_crud.get_user_by_id(db, user_id)
    else:
        user = user_crud.get_user_by_username(db, username)

    if user is None:
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account is inactive",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
