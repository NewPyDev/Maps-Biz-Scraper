"""Authentication middleware for FastAPI"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
import secrets
from config import settings

security = HTTPBasic()


def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)) -> bool:
    """
    Verify HTTP Basic Auth credentials

    Args:
        credentials: HTTP Basic Auth credentials

    Returns:
        True if credentials are valid

    Raises:
        HTTPException: If authentication is required but credentials are invalid
    """
    # Skip auth if disabled
    if not settings.require_auth:
        return True

    # Check if password is configured
    if not settings.admin_password:
        raise HTTPException(
            status_code=500,
            detail="Authentication is enabled but no password is configured. "
            "Please set ADMIN_PASSWORD in .env file.",
        )

    # Verify username and password using constant-time comparison
    correct_username = secrets.compare_digest(
        credentials.username.encode("utf8"), settings.admin_username.encode("utf8")
    )
    correct_password = secrets.compare_digest(
        credentials.password.encode("utf8"), settings.admin_password.encode("utf8")
    )

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )

    return True
