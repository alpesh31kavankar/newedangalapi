# app/routes/users.py
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, time
import secrets

import os
from fastapi import UploadFile, File
from PIL import Image


UPLOAD_DIR = "uploads/profile_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)
from ..database import get_db
from ..models.user import User
from ..models.email_verification import EmailVerification
from ..models.token import Token
from ..schemas.user import UserCreate, UserOut,UserUpdate  
from passlib.hash import bcrypt
from app.services.email import send_activation_email
from ..routes.auth import get_current_user
from fastapi import Body
router = APIRouter(prefix="/users", tags=["users"])

# ---------------- Utility Functions ---------------- #

def generate_activation_token():
    """Generate random token for email verification."""
    return secrets.token_urlsafe(32)

def generate_referral_code(db: Session):
    """Generate unique 8-character referral code."""
    while True:
        code = secrets.token_hex(4).upper()
        if not db.query(User).filter(User.referral_code == code).first():
            return code

def generate_winning_token(db: Session):
    """Generate sequential winning token ID in WYYYYMMDDXXXX format."""
    now = datetime.now()
    # Determine today or tomorrow based on 8 PM cutoff
    if now.time() >= time(20, 0):
        token_date = (now + timedelta(days=1)).strftime("%Y%m%d")
    else:
        token_date = now.strftime("%Y%m%d")

    prefix = f"W{token_date}"

    # Get last token of today
    last_token = (
        db.query(Token)
        .filter(Token.token_id.like(f"{prefix}%"))
        .order_by(Token.token_id.desc())
        .first()
    )

    if last_token:
        last_number = int(last_token.token_id[-4:])
        new_number = f"{last_number + 1:04d}"
    else:
        new_number = "0001"

    return f"{prefix}{new_number}"


@router.get("/me", response_model=UserOut)
def get_my_profile(current_user: User = Depends(get_current_user)):
    """
    Return the currently logged-in user profile.
    """
    return current_user


 
# ---------------- Referral Validation ---------------- #

@router.get("/validate-referral/{code}")
def validate_referral(code: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.referral_code == code).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid referral code")
    return {"valid": True, "message": "Referral code applied successfully"}

# ---------------- User Registration ---------------- #

@router.post("/register", response_model=UserOut)
def create_user(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Check if email exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    referred_by_code = None
    referred_user = None

    # Check referral
    if user.referral_code:
        referred_user = db.query(User).filter(User.referral_code == user.referral_code).first()
        if not referred_user:
            raise HTTPException(status_code=400, detail="Invalid referral code")
        referred_by_code = user.referral_code

    # Hash password
    hashed_password = bcrypt.hash(user.password)

    # Generate new referral code
    new_referral_code = generate_referral_code(db)

    # Create new user
    db_user = User(
        username=user.username,
        email=user.email,
        password_hash=hashed_password,
        gender=user.gender,
        birth_date=user.birth_date,
        pincode=user.pincode,
        referral_code=new_referral_code,
        referred_by=referred_by_code,
        mobile_no=user.mobile_no or None,
        profile_image=user.profile_image,
        address=user.address,
        is_verified=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # ---------------- Referral Token Logic ---------------- #
    if referred_user:
        # Generate tokens safely in sequence
        tokens_to_create = []

        # 1 token for new user
        base_token_id = generate_winning_token(db)
        tokens_to_create.append(Token(
            token_id=base_token_id,
            users_id=db_user.id,
            token_type="W",
            source="C_referral"
        ))

        # 2 tokens for referrer
        last_number = int(base_token_id[-4:])
        for _ in range(2):
            last_number += 1
            next_token_id = f"{base_token_id[:-4]}{last_number:04d}"
            tokens_to_create.append(Token(
                token_id=next_token_id,
                users_id=referred_user.id,
                token_type="W",
                source="referral_bonus"
            ))

        db.add_all(tokens_to_create)
        db.commit()

    # ---------------- Email Verification ---------------- #
    email_token = generate_activation_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)
    verification = EmailVerification(
        users_id=db_user.id,
        token=email_token,
        expires_at=expires_at,
        is_used=False
    )
    db.add(verification)
    db.commit()

    # Send activation email
    activation_link = f"http://localhost:4200/basic/activate?token={email_token}"
    background_tasks.add_task(send_activation_email, db_user.email, activation_link)

    # Return user
    return UserOut(
        id=db_user.id,
        email=db_user.email,
        username=db_user.username,
        is_verified=db_user.is_verified,
        referral_code=db_user.referral_code,
        referred_by=db_user.referred_by,
        address=db_user.address,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
        activation_link=activation_link  # For testing
    )

# ---------------- Activate Account ---------------- #

@router.post("/{user_id}/upload-profile-image")
def upload_profile_image(
    user_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Only allow image files
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type")

    # Generate unique filename
    ext = file.filename.split(".")[-1]
    filename = f"user_{user_id}_{int(datetime.utcnow().timestamp())}.{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    # Resize image
    try:
        image = Image.open(file.file)
        image.thumbnail((400, 400))  # resize max 400x400
        image.save(filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image processing error: {str(e)}")

    # Update user in DB
    user.profile_image = filename
    db.commit()
    db.refresh(user)

    return {"filename": filename, "message": "Profile image uploaded successfully"}   



@router.get("/activate")
def activate_user(token: str, db: Session = Depends(get_db)):
    verification = db.query(EmailVerification).filter(EmailVerification.token == token).first()
    if not verification:
        raise HTTPException(status_code=400, detail="Invalid activation token")
    if verification.is_used:
        raise HTTPException(status_code=400, detail="Token already used")
    if verification.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Activation token expired")

    verification.is_used = True
    user = db.query(User).filter(User.id == verification.users_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_verified = True

    db.commit()
    return {"message": "Account activated successfully"}

# ---------------- Get Users ---------------- #

@router.get("/my-referral-code")
def my_referral_code(current_user: User = Depends(get_current_user)):
    return {"referral_code": current_user.referral_code}

@router.get("/my-referrals-detail")
def get_my_referrals_detail(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Show:
    1. List of users who used my referral code
    2. List of referral_bonus tokens I have
    """
    # Users who used my referral code
    referrals = db.query(User).filter(User.referred_by == current_user.referral_code).order_by(User.created_at.desc()).all()
    referral_users = [
        {
            "user_id": u.id,
            "username": u.username,
            "created_at": u.created_at
        }
        for u in referrals
    ]

     # Get today's date in YYYYMMDD format
    today_str = datetime.now().strftime("%Y%m%d")
    prefix = f"W{today_str}"

    # Tokens with source 'referral_bonus' and today's date in token_id
    tokens = db.query(Token).filter(
        Token.users_id == current_user.id,
        Token.source == "referral_bonus",
        Token.token_id.like(f"{prefix}%")
    ).order_by(Token.created_at.asc()).all()
    referral_tokens = [
        {
            "token_id": t.token_id,
            "created_at": t.created_at,
            "source": t.source
        }
        for t in tokens
    ]

    return {
        "referral_users": referral_users,
        "referral_tokens": referral_tokens,
    }

@router.get("/missed-tokens")
def get_missed_tokens(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Yesterday's date in YYYYMMDD format
    yesterday_str = (datetime.utcnow() - timedelta(days=1)).strftime("%Y%m%d")

    missed = db.query(Token).filter(
        Token.users_id == current_user.id,
        Token.source.in_(["round_win", "referral_bonus"]),
        Token.token_id.like(f"%{yesterday_str}%")
    ).count()

    return {"missed_count": missed}

@router.get("/my-referral-tickets")
def my_referral_ticket_count(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Return number of tickets earned via referral_bonus claimed (C_referral_bonus)"""
    count = db.query(Token).filter(
        Token.users_id == current_user.id,
        Token.source == "C_referral_bonus"
    ).count()
    return {"ticket_count": count}

@router.post("/claim-referral-token/{token_id}")
def claim_referral_token(token_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    token = db.query(Token).filter(Token.token_id == token_id, Token.users_id == current_user.id, Token.source == "referral_bonus").first()
    if not token:
        raise HTTPException(status_code=404, detail="Token not found or already claimed")
    
    token.source = "C_referral_bonus"
    db.commit()
    return {"message": f"Token {token_id} claimed successfully"}

@router.get("/{user_id}", response_model=UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()  # use User, not models.User
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}/update", response_model=UserOut)
def update_user(user_id: int, request: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()  # use User, not models.User

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if request.mobile_no:
        user.mobile_no = request.mobile_no
    if request.address:
        user.address = request.address

    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=list[UserOut])
def get_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return [UserOut.from_orm(u) for u in users]

# @router.get("/{user_id}", response_model=UserOut)
# def get_user(user_id: int, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     return UserOut.from_orm(user)



@router.post("/claim-referral")
def claim_referral(referred_user_id: int = Body(...), current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """
    Claim referral_bonus tokens for a specific referred user.
    """
    # Verify this user actually used my referral code
    referred_user = db.query(User).filter(User.id == referred_user_id, User.referred_by == current_user.referral_code).first()
    if not referred_user:
        raise HTTPException(status_code=400, detail="No referred user found for this claim")

    # Get all tokens for referrer with source referral_bonus
    tokens = db.query(Token).filter(Token.users_id == current_user.id, Token.source == "referral_bonus").all()
    if not tokens:
        raise HTTPException(status_code=400, detail="No referral bonus tokens available to claim")

    for t in tokens:
        t.source = "C_referral_bonus"  # Mark claimed

    db.commit()
    return {"message": "Referral bonus tokens claimed successfully"}

