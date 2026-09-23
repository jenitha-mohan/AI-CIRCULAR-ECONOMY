"""
Authentication API Router
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.location import Location
from backend.app.schemas.user import UserRegister, UserLogin, TokenResponse, UserResponse
from backend.app.dependencies import (
    verify_password,
    get_password_hash,
    create_access_token,
    get_current_user
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=TokenResponse)
def register_user(user_in: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists"
        )

    # Resolve or create location
    location = None
    if user_in.city and user_in.state:
        location = db.query(Location).filter(
            Location.city == user_in.city,
            Location.state == user_in.state
        ).first()
        if not location:
            location = Location(
                city=user_in.city,
                state=user_in.state,
                country="India",
                latitude=user_in.latitude or 11.0168,
                longitude=user_in.longitude or 76.9558
            )
            db.add(location)
            db.flush()

    user = User(
        name=user_in.name,
        email=user_in.email,
        password_hash=get_password_hash(user_in.password),
        role=user_in.role if user_in.role in ["seller", "buyer", "admin"] else "seller",
        phone=user_in.phone,
        organization=user_in.organization,
        business_type=user_in.business_type,
        materials_interested=user_in.materials_interested,
        location_id=location.id if location else None
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization": user.organization,
            "business_type": user.business_type,
            "materials_interested": user.materials_interested,
            "city": location.city if location else None
        }
    }


@router.post("/login", response_model=TokenResponse)
def login_user(login_in: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_in.email).first()
    if not user or not verify_password(login_in.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    token = create_access_token(data={"sub": user.id, "role": user.role})
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role,
            "organization": user.organization,
            "business_type": user.business_type,
            "materials_interested": user.materials_interested,
            "city": user.location.city if user.location else None
        }
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    return current_user
