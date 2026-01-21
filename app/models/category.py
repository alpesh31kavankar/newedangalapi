# app/models/category.py
from sqlalchemy import Column, Integer, Text, DateTime, func,ForeignKey
from ..database import Base  # ✅ use the same Base
from sqlalchemy.orm import relationship

class Category(Base):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True, index=True)
    category_name = Column(Text, unique=True, nullable=False)
    description = Column(Text)
    image_url = Column(Text)
      # parent main category
    maincategory_id = Column(Integer, ForeignKey("main_categories.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    vote_reasons = relationship(
        "CategoryVoteReason",
        back_populates="category",
        cascade="all, delete-orphan"
    )