from sqlalchemy import Column, Integer, BigInteger, String, Boolean, DateTime
from sqlalchemy.sql import func
from ..database import Base

class RewardClaim(Base):
    __tablename__ = "reward_claims"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(BigInteger, nullable=False)
    lottery_id = Column(BigInteger, nullable=False)
    gift_id = Column(BigInteger, nullable=False)
    postal_code = Column(String(20), nullable=False)
    contact_no = Column(String(20), nullable=False)
    address = Column(String(255), nullable=False)
    is_claimed = Column(Boolean, default=True)
    claim_type = Column(String(20), default="winning")  # 'winning' or 'participant'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
