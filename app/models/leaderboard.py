from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database import Base

class Leaderboard(Base):
    __tablename__ = "leaderboard"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    month = Column(String, index=True)
    score = Column(Float, default=0)
    claimed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="leaderboards")
