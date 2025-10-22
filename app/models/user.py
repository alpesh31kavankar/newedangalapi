
from sqlalchemy import Column, BigInteger, String, Boolean, Date, Text, TIMESTAMP
from sqlalchemy.sql import func
from ..database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(BigInteger, primary_key=True, index=True)
    username = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True, index=True)
    password_hash = Column(Text, nullable=False)
    gender = Column(String(10))
    birth_date = Column(Date, nullable=False)
    pincode = Column(String(12), nullable=False)
    referral_code = Column(String(20), unique=True)
    referred_by = Column(String(20))
    profile_image = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    mobile_no = Column(String(15), unique=True, nullable=True)
        # 🔑 Email verification
    is_verified = Column(Boolean, default=False)
    # activation_token = Column(Text, nullable=True, index=True)
    # activation_token_expires_at = Column(TIMESTAMP(timezone=True), nullable=True)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    
    verifications = relationship("EmailVerification", back_populates="user", cascade="all, delete-orphan")
        # ✅ Add this for Leaderboard
    leaderboards = relationship("Leaderboard", back_populates="user", cascade="all, delete-orphan")