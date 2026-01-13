from fastapi import APIRouter, Depends, HTTPException, status,Form,Body
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta, time
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
from ..models.token import Token

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


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not bcrypt.verify(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.is_verified:
        raise HTTPException(status_code=403, detail="Account not verified")

    access_token = create_access_token({"user_id": user.id})
    return {"access_token": access_token, "token_type": "bearer"}



# @router.post("/google")
# def google_login(payload: dict = Body(...), db: Session = Depends(get_db)):
#     """
#     Google login/signup endpoint.
#     - If user exists → login
#     - If user new → signup
#     - Referral tokens awarded only once
#     """
#     id_token_str = payload.get("token")
#     referral_code = payload.get("referral_code")  # optional

#     if not id_token_str:
#         raise HTTPException(status_code=400, detail="Missing Google token")

#     try:
#         # ---------------- VERIFY GOOGLE TOKEN ----------------
#         verified_payload = id_token.verify_oauth2_token(
#             id_token_str,
#             requests.Request(),
#             GOOGLE_CLIENT_ID,
#             clock_skew_in_seconds=10
#         )

#         email = verified_payload.get("email")
#         name = verified_payload.get("name", "User")
#         picture = verified_payload.get("picture")

#         if not email:
#             raise HTTPException(status_code=400, detail="Email not found in Google token")

#         # ---------------- CHECK IF USER EXISTS ----------------
#         user = db.query(User).filter(User.email == email).first()

#         if user:
#             # ---------------- EXISTING USER ----------------
#             # Give referral tokens only once
#             if user.referred_by and not getattr(user, "referral_reward_given", False):
#                 referred_user = db.query(User).filter(
#                     User.referral_code == user.referred_by
#                 ).first()

#                 if referred_user:
#                     tokens = []

#                     base_token_id = generate_winning_token(db)

#                     # 1 token for the user
#                     tokens.append(Token(
#                         token_id=base_token_id,
#                         users_id=user.id,
#                         token_type="W",
#                         source="C_referral"
#                     ))

#                     # 2 tokens for the referrer
#                     last_number = int(base_token_id[-4:])
#                     for _ in range(2):
#                         last_number += 1
#                         tokens.append(Token(
#                             token_id=f"{base_token_id[:-4]}{last_number:04d}",
#                             users_id=referred_user.id,
#                             token_type="W",
#                             source="referral_bonus"
#                         ))

#                     db.add_all(tokens)
#                     user.referral_reward_given = True
#                     db.commit()

#             # ---------------- GENERATE ACCESS TOKEN ----------------
#             access_token = create_access_token({"user_id": user.id})
#             return {
#                 "access_token": access_token,
#                 "token_type": "bearer",
#                 "user": {
#                     "id": user.id,
#                     "name": user.username,
#                     "email": user.email,
#                     "profile_image": user.profile_image,
#                     "referral_code": user.referral_code,
#                 }
#             }

#         # ---------------- NEW USER SIGNUP ----------------
#         referred_user = None
#         referred_by_code = None

#         if referral_code:
#             referred_user = db.query(User).filter(User.referral_code == referral_code).first()
#             if not referred_user:
#                 raise HTTPException(status_code=400, detail="Invalid referral code")
#             referred_by_code = referral_code

#         new_referral_code = generate_referral_code(db)

#         user = User(
#             username=name,
#             email=email,
#             password_hash=bcrypt.hash(secrets.token_hex(8)),
#             gender=None,
#             birth_date=date(2000, 1, 1),
#             pincode=000000,
#             referral_code=new_referral_code,
#             referred_by=referred_by_code,
#             profile_image=picture,
#             address=None,
#             mobile_no=None,
#             is_verified=True,
#         )

#         db.add(user)
#         db.commit()
#         db.refresh(user)

#         # ---------------- REFERRAL TOKEN LOGIC FOR NEW USER ----------------
#         if referred_user:
#             tokens_to_create = []

#             base_token_id = generate_winning_token(db)

#             # 1 token for new user
#             tokens_to_create.append(Token(
#                 token_id=base_token_id,
#                 users_id=user.id,
#                 token_type="W",
#                 source="C_referral"
#             ))

#             # 2 tokens for referrer
#             last_number = int(base_token_id[-4:])
#             for _ in range(2):
#                 last_number += 1
#                 next_token_id = f"{base_token_id[:-4]}{last_number:04d}"
#                 tokens_to_create.append(Token(
#                     token_id=next_token_id,
#                     users_id=referred_user.id,
#                     token_type="W",
#                     source="referral_bonus"
#                 ))

#             db.add_all(tokens_to_create)
#             user.referral_reward_given = True
#             db.commit()

#         # ---------------- GENERATE ACCESS TOKEN ----------------
#         access_token = create_access_token({"user_id": user.id})
#         return {
#             "access_token": access_token,
#             "token_type": "bearer",
#             "user": {
#                 "id": user.id,
#                 "name": user.username,
#                 "email": user.email,
#                 "profile_image": user.profile_image,
#                 "referral_code": user.referral_code,
#             }
#         }

#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid Google token")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@router.post("/google")
def google_login(payload: dict = Body(...), db: Session = Depends(get_db)):
    """
    Google login/signup endpoint.
    - Existing user → just login
    - New user → signup and give referral tokens if referral_code provided
    """
    id_token_str = payload.get("token")
    referral_code = payload.get("referral_code")

    if not id_token_str:
        raise HTTPException(status_code=400, detail="Missing Google token")

    try:
        verified_payload = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )

        email = verified_payload.get("email")
        name = verified_payload.get("name", "User")
        picture = verified_payload.get("picture")

        if not email:
            raise HTTPException(status_code=400, detail="Email not found in Google token")

        # ---------------- CHECK IF USER EXISTS ----------------
        user = db.query(User).filter(User.email == email).first()

        if user:
            # Existing user → no referral tokens, just login
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
                }
            }

        # ---------------- NEW USER SIGNUP ----------------
        referred_user = None
        referred_by_code = None

        if referral_code:
            referred_user = db.query(User).filter(User.referral_code == referral_code).first()
            if not referred_user:
                raise HTTPException(status_code=400, detail="Invalid referral code")
            referred_by_code = referral_code

        new_referral_code = generate_referral_code(db)

        user = User(
            username=name,
            email=email,
            password_hash=bcrypt.hash(secrets.token_hex(8)),
            gender=None,
            birth_date=date(2000, 1, 1),
            pincode=0,
            referral_code=new_referral_code,
            referred_by=referred_by_code,
            profile_image=picture,
            address=None,
            mobile_no=None,
            is_verified=True,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        # ---------------- GIVE REFERRAL TOKENS ONLY FOR NEW USER ----------------
        if referred_user:
            tokens_to_create = []

            base_token_id = generate_winning_token(db)

            # 1 token for new user
            tokens_to_create.append(Token(
                token_id=base_token_id,
                users_id=user.id,
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

        # ---------------- GENERATE ACCESS TOKEN ----------------
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
            }
        }

    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")



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
