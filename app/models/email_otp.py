# models/email_otp.py
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base

class EmailOTP(Base):
    __tablename__ = "email_otps"

    id = Column(BigInteger, primary_key=True, index=True)
    users_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    otp_code = Column(String(6), nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
