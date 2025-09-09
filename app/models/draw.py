from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.database import Base

class Draw(Base):
    __tablename__ = "draws"

    draw_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    result_time = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
