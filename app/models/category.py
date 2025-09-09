# app/models/category.py
from sqlalchemy import Column, Integer, String, Text
from app.database import Base

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, index=True)
    category_name = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)
    icon_url = Column(Text, nullable=True)
    image_url = Column(Text, nullable=True)
