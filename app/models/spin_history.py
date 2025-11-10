from sqlalchemy import Column, Integer, ForeignKey, String, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class SpinHistory(Base):
    __tablename__ = "spin_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    prize_type = Column(String(20), nullable=False)
    prize_value = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

     # ✅ Match the back_populates name
    user = relationship("User", back_populates="spins")
