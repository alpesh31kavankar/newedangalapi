from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from ..database import get_db
from ..models import user, email_otp
from ..schemas.forgot_password_schema import ForgotPasswordRequest, ResetPasswordRequest,VerifyOtpRequest
from ..services.email import send_otp_email
from ..utils import hash_password

router = APIRouter(
    prefix="/forgot-password",
    tags=["Forgot Password"]
)

@router.post("/request")
def forgot_password_request(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    existing_user = db.query(user.User).filter(user.User.email == payload.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    otp = str(random.randint(100000, 999999))
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    new_otp = email_otp.EmailOTP(
        users_id=existing_user.id,
        otp_code=otp,
        expires_at=expires_at
    )
    db.add(new_otp)
    db.commit()

    # ✅ Pass username here
    send_otp_email(existing_user.email, otp, existing_user.username)

    return {"message": "OTP sent to your email"}



# ✅ Step 2: Verify OTP and reset password
@router.post("/reset")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    existing_user = db.query(user.User).filter(user.User.email == payload.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_entry = db.query(email_otp.EmailOTP).filter(
        email_otp.EmailOTP.users_id == existing_user.id,
        email_otp.EmailOTP.otp_code == payload.otp_code,
        email_otp.EmailOTP.is_used == False,
        email_otp.EmailOTP.expires_at > datetime.utcnow()
    ).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    existing_user.password_hash = hash_password(payload.new_password)
    otp_entry.is_used = True
    db.commit()

    return {"message": "Password reset successful"}

@router.post("/verify")
def verify_otp(payload: VerifyOtpRequest, db: Session = Depends(get_db)):
    existing_user = db.query(user.User).filter(user.User.email == payload.email).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    otp_entry = db.query(email_otp.EmailOTP).filter(
        email_otp.EmailOTP.users_id == existing_user.id,
        email_otp.EmailOTP.otp_code == payload.otp_code,
        email_otp.EmailOTP.is_used == False,
        email_otp.EmailOTP.expires_at > datetime.utcnow()
    ).first()

    if not otp_entry:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")

    return {"message": "OTP verified successfully"}
