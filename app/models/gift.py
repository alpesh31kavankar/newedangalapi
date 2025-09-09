# app/models/gift.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, CheckConstraint, TIMESTAMP, func
from sqlalchemy.orm import relationship
from app.database import Base

class Gift(Base):
    __tablename__ = "gifts"

    gift_id = Column(Integer, primary_key=True, index=True)
    draw_id = Column(Integer, ForeignKey("draws.draw_id", ondelete="CASCADE"), nullable=False)
    gift_type = Column(String(20), nullable=False)  # participant / winning
    gift_name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
    quantity = Column(Integer, default=1)
    created_at = Column(TIMESTAMP, server_default=func.now())
    is_active = Column(Boolean, default=True)

    __table_args__ = (
        CheckConstraint("gift_type IN ('participant', 'winning')", name="gift_type_check"),
    )

    # relationship back to draw (optional)
    draw = relationship("Draw", backref="gifts")
