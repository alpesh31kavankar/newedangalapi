# app/models/email_verification.py
from sqlalchemy import Column, BigInteger, String, Boolean, TIMESTAMP, ForeignKey
from sqlalchemy.sql import func
from ..database import Base
from sqlalchemy.orm import relationship

class EmailVerification(Base):
    __tablename__ = "email_verifications"

    id = Column(BigInteger, primary_key=True, index=True)
    users_id = Column(BigInteger, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(255), unique=True, nullable=False)
    expires_at = Column(TIMESTAMP(timezone=True), nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    # ORM relationship
    user = relationship("User", back_populates="verifications")