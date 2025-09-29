# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.schemas.user import UserCreate, UserResponse
# from app.models.user import User
# from app.database import get_db
# from app.core.security import hash_password


# router = APIRouter(
#     prefix="/users",
#     tags=["users"]
# )

# @router.post("/", response_model=UserResponse)
# def create_user(user: UserCreate, db: Session = Depends(get_db)):
#     print("📥 Incoming user data:", user.dict())
#     if db.query(User).filter(User.email == user.email).first():
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     if db.query(User).filter(User.username == user.username).first():
#         raise HTTPException(status_code=400, detail="Username already taken")

#     new_user = User(
#         username=user.username,
#         email=user.email,
#         password_hash=hash_password(user.password),
#         full_name=user.full_name,
#         phone_number=user.phone_number,
#         address=user.address
#     )
#     db.add(new_user)
#     db.commit()
#     db.refresh(new_user)
#     return new_user


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.user import UserCreate, UserOut
from passlib.hash import bcrypt

router = APIRouter(prefix="/users", tags=["users"])

# Create new user
@router.post("/", response_model=UserOut)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Hash password
    hashed_password = bcrypt.hash(user.password)

    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        gender=user.gender,
        birth_date=user.birth_date,
        pincode=user.pincode,
        referral_code=user.referral_code,
        referred_by=user.referred_by,
        mobile_no=user.mobile_no,
        profile_image=user.profile_image,
        address=user.address
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get all users
@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Get single user by ID
@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
