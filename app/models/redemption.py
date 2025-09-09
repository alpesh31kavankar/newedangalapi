# app/models/redemption.py
from sqlalchemy import Column, Integer, ForeignKey, String, Text, DateTime, func
from app.database import Base

class Redemption(Base):
    __tablename__ = 'redemptions'

    redemption_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    draw_id = Column(Integer, ForeignKey("draws.draw_id"))
    product_id = Column(Integer, ForeignKey("products.product_id"))
    address = Column(Text)
    phone_number = Column(String(20))
    redeemed_at = Column(DateTime, server_default=func.now())
    status = Column(String(20), default="pending")  # pending, shipped, delivered
