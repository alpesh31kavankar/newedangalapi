# app/models/user_ad.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Boolean, func
from app.database import Base

class UserAd(Base):
    __tablename__ = 'user_ads'

    ad_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    watched_at = Column(DateTime, server_default=func.now())
    next_available_at = Column(DateTime)
    rewarded_token = Column(Boolean, default=False)
