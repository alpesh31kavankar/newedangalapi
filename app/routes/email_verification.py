# app/routes/email_verification.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
import secrets

from .. import models, schemas
from ..database import get_db


router = APIRouter(
    prefix="/email-verification",
    tags=["Email Verification"]
)

# Utility function to generate token
def generate_token():
    return secrets.token_urlsafe(32)


# 1️⃣ Create verification record (called after register)
@router.post("/create/{user_id}")
def create_verification(user_id: int, db: Session = Depends(get_db)):
    token = generate_token()
    expires_at = datetime.utcnow() + timedelta(hours=24)

    verification = models.EmailVerification(
        users_id=user_id,
        token=token,
        expires_at=expires_at,
        is_used=False
    )
    db.add(verification)
    db.commit()
    db.refresh(verification)

    # TODO: call your send_email utility here
    # send_email(user.email, f"Click to activate: https://yourfrontend.com/activate?token={token}")

    return {"message": "Verification created, email sent", "token": token}


# 2️⃣ Verify email by token
@router.get("/activate/{token}")
def activate_email(token: str, db: Session = Depends(get_db)):
    verification = db.query(models.EmailVerification).filter(
        models.EmailVerification.token == token
    ).first()

    if not verification:
        raise HTTPException(status_code=404, detail="Invalid token")

    if verification.is_used:
        raise HTTPException(status_code=400, detail="Token already used")

    if verification.expires_at < datetime.now(timezone.utc):  # ✅ timezone-aware
        raise HTTPException(status_code=400, detail="Token expired")

    # Mark verification as used
    verification.is_used = True
    verification.updated_at = datetime.now(timezone.utc)  # ✅ timezone-aware

    # Also mark user as verified
    user = db.query(models.User).filter(models.User.id == verification.users_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.is_verified = True

    db.commit()

    return {"message": "Email verified successfully"}