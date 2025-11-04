from fastapi import APIRouter, Depends, HTTPException, status,Form,Body
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from ..database import get_db
from ..models.user import User
from app.models.admin import AdminRegistration
from ..services.jwt import create_access_token, verify_token
from typing import Optional
from jose import JWTError
from google.oauth2 import id_token
from google.auth.transport import requests 
import secrets 
from ..services.jwt import create_access_token, verify_token
from datetime import date

# from ..utils.jwt import create_access_token
GOOGLE_CLIENT_ID = "604482246960-37qevscc0kgssnoflqi6kkam69jvilur.apps.googleusercontent.com"

router = APIRouter(prefix="/auth", tags=["Authentication"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# ✅ Moved here to avoid circular import
def generate_referral_code(db: Session):
    """Generate unique 8-character referral code."""
    while True:
        code = secrets.token_hex(4).upper()
        if not db.query(User).filter(User.referral_code == code).first():
            return code

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified")

    access_token = create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}



@router.post("/google")
def google_login(payload: dict = Body(...), db: Session = Depends(get_db)):
    print("📩 Received payload:", payload)

    id_token_str = payload.get("token")
    if not id_token_str:
        raise HTTPException(status_code=400, detail="Missing token")

    try:
        # ✅ Correct verification
        verified_payload = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            GOOGLE_CLIENT_ID
        )
        print("✅ Verified Google payload:", verified_payload)

        email = verified_payload.get("email")
        name = verified_payload.get("name", "User")
        picture = verified_payload.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in Google token")

        # ✅ Find or create user
        user = db.query(User).filter(User.email == email).first()

        if not user:
            new_referral_code = generate_referral_code(db)

            user = User(
                username=name,
                email=email,
                password_hash=bcrypt.hash(secrets.token_hex(8)),
                gender=None,
                birth_date=date(2000, 1, 1),
                pincode=000000,
                referral_code=new_referral_code,
                referred_by=None,
                profile_image=picture,
                address=None,
                mobile_no=None,
                is_verified=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ Created new Google user: {email}")

        # ✅ Generate JWT
        access_token = create_access_token({"user_id": user.id})

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "name": user.username,
                "email": user.email,
                "profile_image": user.profile_image,
                "referral_code": user.referral_code,
            },
        }

    except ValueError as ve:
        print("❌ ValueError verifying token:", str(ve))
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {ve}")
    except Exception as e:
        print("🔥 Unexpected error verifying token:", e)
        raise HTTPException(status_code=500, detail=str(e))






@router.post("/adminlogin")
def adminlogin(email: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    admin = db.query(AdminRegistration).filter(AdminRegistration.email == email).first()
    if not admin or admin.password != password:  # plain text comparison
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_access_token({"sub": admin.email})
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin": {
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
        }
    }


# Dependency to get current user from token
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user



# Optional user dependency — does NOT raise 401
def get_current_user_optional(
    token: Optional[str] = Depends(OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)),
    db: Session = Depends(get_db)
):
    if not token:
        return None

    try:
        payload = verify_token(token)
        if not payload:
            return None
    except JWTError:
        return None

    user = db.query(User).filter(User.id == payload.get("user_id")).first()
    return user
