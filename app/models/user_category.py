# app/models/user_category.py
from sqlalchemy import Column, Integer, ForeignKey, DateTime, func
from app.database import Base

class UserCategory(Base):
    __tablename__ = 'user_categories'

    user_category_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"))
    selected_at = Column(DateTime(timezone=False), server_default=func.now())
