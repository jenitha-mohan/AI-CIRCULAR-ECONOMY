"""
Authentication API Router
Handles user registration with password strength enforcement, secure login, and safe profile inspection.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User, UserRole
from backend.app.models.location import Location
from backend.app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from backend.app.dependencies import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user,
    log_security_event
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    """
    Registers a new user (Seller or Buyer) with hashed passwords and profile setup.
    Enforces email uniqueness, role constraints, and password complexity.
    """
    existing = db.query(User).filter(User.email.ilike(user_in.email.strip())).first()
    if existing:
        log_security_event("REGISTER_DUPLICATE_EMAIL", detail=f"Email '{user_in.email}' already exists")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists."
        )

    # Normalize role
    role_member = UserRole.from_str(user_in.role)
    role_val = role_member.value

    # Organization / company name
    company = user_in.get_company_name()

    # Resolve or create location
    location = None
    if user_in.city and user_in.state:
        location = db.query(Location).filter(
            Location.city.ilike(user_in.city.strip()),
            Location.state.ilike(user_in.state.strip())
        ).first()
        if not location:
            location = Location(
                city=user_in.city.strip(),
                state=user_in.state.strip(),
                country=user_in.country or "India",
                latitude=user_in.latitude or 11.0168,
                longitude=user_in.longitude or 76.9558
            )
            db.add(location)
            db.flush()

    user = User(
        name=user_in.name,
        email=user_in.email.strip().lower(),
        password_hash=get_password_hash(user_in.password),
        role=role_val,
        phone=user_in.phone,
        organization=company,
        business_type=user_in.business_type,
        materials_interested=user_in.materials_interested,
        location_id=location.id if location else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_security_event("REGISTER_SUCCESS", user_id=user.id, detail=f"Registered role={user.role}")

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_safe_dict()
    }


@router.post("/login", response_model=TokenResponse)
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    """
    Authenticates user via email and bcrypt hash verification.
    Generates a signed, expiring JWT with role claims.
    """
    user = db.query(User).filter(User.email.ilike(login_in.email.strip())).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        log_security_event("LOGIN_FAILED", detail=f"Failed login attempt for email '{login_in.email}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    log_security_event("LOGIN_SUCCESS", user_id=user.id, detail=f"Role={user.role}")

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user.to_safe_dict()
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Returns the sanitized profile of the currently authenticated user.
    Never reveals password_hash or internal secrets.
    """
    return current_user
