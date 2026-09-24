"""
Authentication, RBAC & Security Dependencies
Enforces stateless JWT validation, bcrypt password hashing, and role-based access control.
"""

import bcrypt
import logging
from datetime import datetime, timedelta
from typing import Optional, List, Union
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, ExpiredSignatureError, jwt
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.database import get_db
from backend.app.models.user import User

logger = logging.getLogger("circular_economy.security")
security = HTTPBearer(auto_error=False)


def log_security_event(event_type: str, user_id: Optional[str] = None, detail: str = ""):
    """Audit log security events without recording passwords or secrets."""
    logger.info(f"[SECURITY_AUDIT] event={event_type} user_id={user_id or 'anonymous'} detail={detail}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against the stored bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8")[:72],
            hashed_password.encode("utf-8")
        )
    except Exception as e:
        logger.warning(f"Password verification failure: {e}")
        return False


def get_password_hash(password: str) -> str:
    """Generates a secure bcrypt hash for a plaintext password."""
    pwd_bytes = password.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(pwd_bytes, salt).decode("utf-8")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Generates a signed JWT with subject ID, role, and expiration."""
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def get_current_user(
    auth: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Extracts Bearer JWT from Authorization header, validates signature and expiration,
    and loads the authenticated user from the database.
    """
    if not auth or not auth.credentials:
        log_security_event("AUTH_MISSING_TOKEN", detail="No Bearer token provided in request")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(
            auth.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            log_security_event("AUTH_INVALID_PAYLOAD", detail="Missing subject in JWT payload")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except ExpiredSignatureError:
        log_security_event("AUTH_EXPIRED_TOKEN", detail="JWT token has expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        log_security_event("AUTH_JWT_ERROR", detail=f"JWT validation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        log_security_event("AUTH_USER_NOT_FOUND", user_id=user_id, detail="User in JWT does not exist")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User account not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_role(allowed_roles: Union[List[str], str]):
    """
    Dependency factory to enforce Role-Based Access Control (RBAC).
    Returns the authenticated user if their role is in allowed_roles, otherwise raises 403 Forbidden.
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]
    normalized_allowed = [r.lower() for r in allowed_roles]

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role = (current_user.role or "").lower()
        if user_role not in normalized_allowed and user_role != "admin":
            log_security_event(
                "RBAC_FORBIDDEN",
                user_id=current_user.id,
                detail=f"User with role '{user_role}' attempted access requiring {normalized_allowed}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You are not authorized to perform this operation. Required role: {', '.join(allowed_roles).upper()}."
            )
        return current_user

    return role_checker
