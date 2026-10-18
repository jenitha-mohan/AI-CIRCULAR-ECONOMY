from typing import List, Union
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models.user import User
from backend.app.models.location import Location
from backend.app.schemas.user import UserResponse, UserPublicResponse, UserUpdate
from backend.app.dependencies import get_current_user, require_role

router = APIRouter(prefix="/api/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_user_profile(current_user: User = Depends(get_current_user)):
    """Retrieve authenticated user's own full profile with contact details."""
    return current_user


@router.put("/me", response_model=UserResponse)
@router.patch("/me", response_model=UserResponse)
def update_my_user_profile(
    user_in: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update approved profile fields (phone, organization, business_type, location).
    User identity is strictly derived from the JWT.
    Privileged fields (id, role, password_hash, email) cannot be altered.
    """
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    if user_in.organization is not None:
        current_user.organization = user_in.organization
        current_user.company_name = user_in.organization
    if user_in.business_type is not None:
        current_user.business_type = user_in.business_type

    # Location updates
    if user_in.city is not None or user_in.state is not None:
        if current_user.location:
            if user_in.city is not None:
                current_user.location.city = user_in.city
            if user_in.state is not None:
                current_user.location.state = user_in.state
        else:
            new_loc = Location(
                city=user_in.city or "Coimbatore",
                state=user_in.state or "Tamil Nadu",
                country="India"
            )
            db.add(new_loc)
            db.flush()
            current_user.location_id = new_loc.id

    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin_user: User = Depends(require_role(["admin"]))
):
    """Admin-only: Retrieve all system users with full attributes."""
    return db.query(User).order_by(User.created_at.desc()).all()


@router.get("/{user_id}", response_model=Union[UserResponse, UserPublicResponse])
def get_user_by_id(
    user_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve user profile details.
    If requester is the user themselves or an admin, returns full UserResponse with contact information.
    Otherwise, returns limited UserPublicResponse to protect personal information (email, phone).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Full profile for owner or admin
    if current_user.id == user.id or current_user.role == "admin":
        return user

    # Anonymized / limited public profile for other marketplace participants
    return UserPublicResponse(
        id=user.id,
        name=user.name,
        role=user.role,
        organization=user.organization,
        company_name=user.company_name,
        business_type=user.business_type,
        location=user.location,
        created_at=user.created_at
    )

