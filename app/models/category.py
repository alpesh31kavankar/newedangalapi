# app/models/category.py
from sqlalchemy import Column, Integer, Text, DateTime, func
from ..database import Base  # ✅ use the same Base

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(Text)
    round_interval_minutes = Column(Integer, nullable=False, default=30)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
