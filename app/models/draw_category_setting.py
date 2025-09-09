# app/models/draw_category_setting.py
from sqlalchemy import Column, Integer, ForeignKey
from app.database import Base

class DrawCategorySetting(Base):
    __tablename__ = 'draw_category_settings'

    setting_id = Column(Integer, primary_key=True, index=True)
    draw_id = Column(Integer, ForeignKey("draws.draw_id", ondelete="CASCADE"))
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="CASCADE"))
    num_questions = Column(Integer, nullable=False)
    interval_minutes = Column(Integer, nullable=False)
